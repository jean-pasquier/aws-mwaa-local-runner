import os
from datetime import datetime

import pendulum
from airflow import DAG
from airflow.models import Connection
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from project.conf.config import get_config

parameters = get_config("parameters")

# DAG metadata

# By convention, the dag name must be the same as the name of the .py file
DAG_NAME = os.path.basename(__file__).split(".")[0]

# By convention, the dag id must be : <team>_<project>_<dag_name>
DAG_ID = parameters["dag_id_template"].format(dag_name=DAG_NAME)


# time zone info ( allows the cron to be in the selected timezone )
LOCAL_TZ = pendulum.timezone(parameters["default_timezone"])


def _connect_redshift():
    rsh = Connection("rsh_conn_test")
    print(rsh.host)
    print(rsh.login)


with DAG(
        dag_id=DAG_ID,
        description="Test redshift connection",
        start_date=datetime(2021, 1, 1, tzinfo=LOCAL_TZ),
        schedule_interval="@once",
        catchup=False,
        tags=parameters["default_dag_parameters"]["tags"],
        default_args=parameters["default_args"]
) as dag:
    co = PythonOperator(task_id="connect_redshift", python_callable=_connect_redshift)

    co >> S3ToRedshiftOperator(
        task_id='s3_to_redshift',
        schema='cds',
        table='f_transport_upstream_co2_pmt',
        s3_bucket='bucket',
        s3_key='path/to/year=2022/month=8/day=4/',
        redshift_conn_id='rsh_conn_test',
        aws_conn_id='aws_conn_test',
        copy_options=[
            "FORMAT AS PARQUET"
        ],
        method='UPSERT',
        upsert_keys=["leg_type","reception_date","containor_id","containor_number","order_as"]
    )
