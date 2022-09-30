import datetime as dt

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


def _list_keys(bucket_name: str, region_name: str = "eu-west-1"):
    s3_hook = S3Hook(aws_conn_id="aws_conn_test", region_name=region_name)
    bucket_exists = s3_hook.check_for_bucket(bucket_name)
    print(f"{bucket_name} exists ? {bucket_exists}")
    print("\n".join(s3_hook.list_keys(bucket_name)))


with DAG(
        dag_id="test_minio",
        schedule_interval="@once",
        start_date=dt.datetime(2021, 12, 1, 0, 0, 0),
        is_paused_upon_creation=False) as dag:

    op = PythonOperator(task_id="unique_s3_task_1", python_callable=_list_keys, op_args=["bucket",])
    op2 = PythonOperator(task_id="unique_s3_task_2", python_callable=_list_keys, op_kwargs={"bucket_name": "bucket"})

    op >> op2
