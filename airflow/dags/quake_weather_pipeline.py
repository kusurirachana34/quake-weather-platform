from datetime import datetime

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

PY = "/opt/airflow/pipeline_venv/bin/python"
DBT = "/opt/airflow/pipeline_venv/bin/dbt"
PROJECT = "/opt/airflow/project"

with DAG(
    dag_id="quake_weather_pipeline",
    start_date=datetime(2026, 10, 1),
    schedule="@daily",
    catchup=False,
    tags=["portfolio"],
) as dag:
    load_earthquakes = BashOperator(
        task_id="load_earthquakes",
        bash_command=f"cd {PROJECT} && {PY} -m load.load_earthquakes",
    )
    load_weather = BashOperator(
        task_id="load_weather",
        bash_command=f"cd {PROJECT} && {PY} -m load.load_weather",
    )
    dbt_seed = BashOperator(
        task_id="dbt_seed",
        bash_command=f"cd {PROJECT}/transform && {DBT} seed --profiles-dir .",
    )
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {PROJECT}/transform && {DBT} run --profiles-dir .",
    )
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {PROJECT}/transform && {DBT} test --profiles-dir .",
    )

    [load_earthquakes, load_weather] >> dbt_seed >> dbt_run >> dbt_test
