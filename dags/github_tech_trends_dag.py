import os
import shutil
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_BIN = shutil.which("dbt") or "/home/airflow/.local/bin/dbt"
DBT_PROJECT_DIR = os.getenv("DBT_PROJECT_DIR", "/opt/airflow/dbt_project")
DAGS_DIR = "/opt/airflow/dags"

default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'github_tech_trends_pipeline',
    default_args=default_args,
    schedule_interval='0 2 * * *',
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    extract_bronze = BashOperator(
        task_id='extract_bronze',
        bash_command=f'python {DAGS_DIR}/01_extract_bronze.py'
    )

    transform_silver = BashOperator(
        task_id='transform_silver',
        bash_command=f'python {DAGS_DIR}/02_transform_silver.py'
    )

    load_duckdb = BashOperator(
        task_id='load_duckdb',
        bash_command=f'python {DAGS_DIR}/03_load_duckdb.py'
    )

    dbt_run_staging = BashOperator(
        task_id='dbt_run_staging',
        bash_command=f'{DBT_BIN} run --select stg_github_repos --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROJECT_DIR}'
    )

    dbt_test_staging = BashOperator(
        task_id='dbt_test_staging',
        bash_command=f'{DBT_BIN} test --select stg_github_repos --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROJECT_DIR}'
    )

    dbt_run_gold = BashOperator(
        task_id='dbt_run_gold',
        bash_command=f'{DBT_BIN} run --select gold_repo_metrics --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROJECT_DIR}'
    )

    dbt_test_gold = BashOperator(
        task_id='dbt_test_gold',
        bash_command=f'{DBT_BIN} test --select gold_repo_metrics --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROJECT_DIR}'
    )

    extract_bronze >> transform_silver >> load_duckdb >> dbt_run_staging >> dbt_test_staging >> dbt_run_gold >> dbt_test_gold