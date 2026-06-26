import sys
import pendulum
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import timedelta

sys.path.append('/opt/airflow/dags')

def safe_main_callable():
    from insert_record import main
    return main()

default_args = {
    'description': 'A DAG to orchestrate data',
    'start_date': pendulum.datetime(2026, 6, 1, tz="Asia/Ho_Chi_Minh"),
    'catchup': False,
}

dag = DAG(
    dag_id='weather-api-orchestrator',
    default_args=default_args,
    schedule=timedelta(minutes=1)
)

with dag:
    task1 = PythonOperator(
        task_id='example_task',
        python_callable=safe_main_callable
    )
