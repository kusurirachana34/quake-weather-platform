FROM apache/airflow:3.3.0

RUN python -m venv /opt/airflow/pipeline_venv \
 && /opt/airflow/pipeline_venv/bin/pip install --no-cache-dir \
    requests pandas sqlalchemy psycopg2-binary python-dotenv dbt-postgres
