from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.decorators import task
from pipeline.retrain import compare_models, prepare_data, publish_model, train_model


with DAG(
    'train_model',
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
    schedule='2-59/5 * * * *',
    catchup=False,
    max_active_runs=1,
    default_args={'retries': 2, 'retry_delay': timedelta(seconds=15)},
    tags=['fraud'],
) as dag:
    prepared = task.short_circuit(prepare_data)(run_id='{{ run_id }}')
    trained = task(train_model)(prepared)
    compared = task.short_circuit(compare_models)(trained)
    task(publish_model)(compared)
