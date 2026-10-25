from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.decorators import task
from pipeline.supply import append_month, sample_month


with DAG(
    'add_label_batch',
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    schedule='*/5 * * * *',
    catchup=False,
    max_active_runs=1,
    default_args={'retries': 2, 'retry_delay': timedelta(seconds=15)},
    tags=['fraud'],
) as dag:
    sampled = task.short_circuit(sample_month)(run_id='{{ run_id }}')
    task(append_month)(sampled)
