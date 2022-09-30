from typing import List

from airflow import DAG
from airflow.utils.task_group import TaskGroup


class SparkGroup(TaskGroup):
    def __init__(
            self,
            dag: DAG,
            group_id: str,
            cluster_name,
            emr_version,
            emr_conf,
            role_ec2,
            spark_args: List[str],
    ):
        super().__init__(group_id)
        self.dag = dag
        self.cluster_name = cluster_name
        self.emr_version = emr_version
        self.emr_conf = emr_conf
        self.role_ec2 = role_ec2
        self.spark_args = spark_args


