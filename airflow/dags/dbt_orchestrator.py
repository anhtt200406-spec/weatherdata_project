import os
import sys
import pendulum
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
from datetime import timedelta


def safe_main_callable():
    from insert_record import main
    return main()

default_args = {
    'description': 'A DAG to orchestrate data',
    'start_date': pendulum.datetime(2026, 6, 1, tz="Asia/Ho_Chi_Minh"),
    'catchup': False,
}

dag = DAG(
    dag_id='weather-dbt-orchestrator',
    default_args=default_args,
    schedule=timedelta(minutes=1)
)

DBT_MOUNTS = [
    Mount(
        source='/home/theanh/repos/weatherdata_project/dbt/my_project',
        target='/usr/app/my_project',
        type='bind'
    ),
    Mount(
        source='/home/theanh/repos/weatherdata_project/dbt/my_project',
        target='/root/.dbt/',
        type='bind'
    ),
]

DBT_ENV = {
    'DBT_PROFILES_DIR': '/usr/app/my_project',
    'POSTGRES_HOST': 'db',  # dbt luôn chạy trong Docker network, host phải là tên service
    'POSTGRES_USER': os.getenv('POSTGRES_USER'),
    'POSTGRES_PASSWORD': os.getenv('POSTGRES_PASSWORD'),
    'POSTGRES_DB': os.getenv('POSTGRES_DB'),
}

with dag:
    task1 = PythonOperator(
        task_id='example_task',
        python_callable=safe_main_callable
    )
    task2 = DockerOperator(
        task_id='transform_data_task',
        image='ghcr.io/dbt-labs/dbt-postgres:1.9.latest',
        command='run',
        working_dir='/usr/app/my_project',
        mounts=DBT_MOUNTS,
        environment=DBT_ENV,
        network_mode='weatherdata_project_my_network',
        docker_url='unix:///var/run/docker.sock',
        auto_remove='success'
    )

    task3 = DockerOperator(
        task_id='test_data_task',
        image='ghcr.io/dbt-labs/dbt-postgres:1.9.latest',
        command='test',
        working_dir='/usr/app/my_project',
        mounts=DBT_MOUNTS,
        environment=DBT_ENV,
        network_mode='weatherdata_project_my_network',
        docker_url='unix:///var/run/docker.sock',
        auto_remove='success'
    )

    task1 >> task2 >> task3
