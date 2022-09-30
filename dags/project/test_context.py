# add your imports here:
import os

import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.emr_add_steps import EmrAddStepsOperator
from airflow.providers.amazon.aws.operators.emr_create_job_flow import EmrCreateJobFlowOperator
from airflow.utils.task_group import TaskGroup

from project import VERSION  # As defined in VERSION file
from project.conf.config import get_config
from datetime import datetime, timedelta
from airflow.models import Variable

parameters = get_config('parameters')

# DAG metadata

# By convention, the dag name must be the same as the name of the .py file
DAG_NAME = os.path.basename(__file__).split('.')[0]

# By convention, the dag id must be : <team>_<project>_<dag_name>
DAG_ID = parameters['dag_id_template'].format(dag_name=DAG_NAME)

# Conventions to use for 'rs_technical_flow' column if your DAG insert data in RS tables
RS_TECHNICAL_FLOW = parameters['rs_technical_flow_template'].format(
    dag_name=DAG_NAME,
    dag_version=VERSION
)

env = Variable.get('AIRFLOW_ENV', os.getenv("AIRFLOW_ENV", 'local'))

# time zone info ( allows the cron to be in the selected timezone )
LOCAL_TZ = pendulum.timezone(parameters['default_timezone'])


def print_kwargs(**kwargs):
    print(kwargs)
    print("dag_run:", kwargs["dag_run"].__dict__)
    print(kwargs["dag_run"].start_date)


def print_kwargs_task(**kwargs):
    task_id = "step1.p2_with_context" # kwargs["arg_task_id"]
    print(task_id)
    print(kwargs)
    print("dag_run:", kwargs["dag_run"].__dict__)
    ti = kwargs["dag_run"].get_task_instance(task_id=task_id)
    print("task_id:", ti)
    print("task_id:", ti.start_date)

    dt = pendulum.instance(datetime(2021, 1, 1, 17, 3, 0, 0) + timedelta(minutes=5))
    print("is after?", dt > ti.start_date)


# dag definition:
with DAG(
        dag_id=DAG_ID,
        description='Test on EMR',
        start_date=datetime(2021, 1, 1, tzinfo=LOCAL_TZ),
        schedule_interval='@daily',
        catchup=False,
        tags=parameters['default_dag_parameters']['tags'],
        default_args=parameters['default_args']
) as dag:

    create_emr = EmrCreateJobFlowOperator(
        task_id='create_emr',
        cluster_name='my_emr',
        emr_version=parameters['emr_version'],
        app_list=['Spark', 'Ganglia'],
        master_instance_type='r5.2xlarge',
        master_disk_size=64,
        core_instance_type='r5.2xlarge',
        core_on_demand_units=0,
        core_spot_units=2,
        core_disk_size=64,
        role_ec2="EMR_ROLE",
        aws_conn_id='aws_conn_test',
        environment="production" if env == "prod" else "preproduction"
    )

    step_adder = EmrAddStepsOperator(
        task_id='add_steps',
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr', key='return_value') }}",
        steps=[
            {
                'Name': 'run job spark',
                'ActionOnFailure': 'CONTINUE',
                'HadoopJarStep': {
                    'Jar': 'command-runner.jar',
                    'Args': [
                        "spark-submit",
                        "--deploy-mode", parameters["deploy_mode"],
                        "--class", "com.pasquier.jean",
                        "s3://bucket/jars/develop/spark.jar",
                        "-d", datetime.today().strftime('%Y-%m-%d'),
                        "-e", env,
                        "-b", parameters["bucket"],
                        "-m", parameters["master"]
                    ],
                },
            },
        ]
    )

    with TaskGroup(group_id="step1") as step1:
        p1 = PythonOperator(
            task_id='p1',
            python_callable=print_kwargs
        )

        p2 = PythonOperator(
            task_id='p2_with_context',
            provide_context=True,
            python_callable=print_kwargs
        )

        p1 >> p2

    with TaskGroup(group_id="step2") as step2:
        p3 = PythonOperator(
            task_id='p3',
            python_callable=print_kwargs_task,
            # op_kargs={"arg_task_id": "step1.p2_with_context"},
            provide_context=True
        )

        p3

    step1 >> step2
