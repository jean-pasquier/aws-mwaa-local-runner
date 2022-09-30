from typing import Any, List

from airflow.models import BaseOperator
from airflow.providers.amazon.aws.operators.emr_add_steps import EmrAddStepsOperator
from airflow.providers.amazon.aws.sensors.emr_step import EmrStepSensor
from airflow.providers.amazon.aws.operators.emr_create_job_flow import EmrCreateJobFlowOperator


class SparkOnEmr(BaseOperator):

    def __init__(
            self,
            task_id: str,
            cluster_name,
            emr_version,
            emr_conf,
            role_ec2,
            spark_args: List[str],
            **kwargs
    ):
        self.cluster_name = cluster_name
        self.emr_version = emr_version
        self.emr_conf = emr_conf
        self.role_ec2 = role_ec2
        self.spark_args = spark_args
        super().__init__(task_id=task_id, **kwargs)

    def execute(self, context: Any) -> List[EmrStepSensor]:
        create_emr = EmrCreateJobFlowOperator(
            task_id=f'create_emr_{self.cluster_name}',
            cluster_name=self.cluster_name,
            emr_version=self.emr_version,
            app_list=['Spark', 'Ganglia'],
            role_ec2=self.role_ec2,
            aws_conn_id='aws_conn_test'
        )

        job_flow_id = create_emr.execute(context)

        step_ids = EmrAddStepsOperator(
            task_id=f'add_steps_{self.cluster_name}',
            job_flow_id=job_flow_id,
            steps=[
                {
                    'Name': 'run job spark',
                    'ActionOnFailure': 'CONTINUE',
                    'HadoopJarStep': {
                        'Jar': 'command-runner.jar',
                        'Args': ["spark-submit"] + self.spark_args,
                    },
                },
            ]
        ).execute(context)

        return [
            EmrStepSensor(task_id=f'watch_step_{step_id}', job_flow_id=job_flow_id, step_id=step_id)
            for step_id in step_ids
        ]

