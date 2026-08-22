from airflow.sdk import DAG
from airflow.operators.python import PythonOperator

from datetime import timedelta

import requests

default_args = {
    'owner': 'admin',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def status_updater(batch_wise:bool, max_batch:int):
    print(
        f"Starting status update: batch_wise={batch_wise}, max_batch={max_batch}"
    )

    payload = {
        "batch_wise": batch_wise,
        "max_batches": max_batch,
    }

    response = requests.post(
        "http://backend:8000/scraper/status_update_af",
        json=payload,
        timeout=60*20,
    )

    response.raise_for_status()

    print("status update completed")

def metadata_updater(batch_wise:bool, max_batch:int):
    print(
        f"Starting metadata update: batch_wise={batch_wise}, max_batch={max_batch}"
    )

    payload = {
        "batch_wise": batch_wise,
        "max_batches": max_batch,
    }

    response = requests.post(
        "http://backend:8000/scraper/metadata_update_af",
        json=payload,
        timeout=60*30,
    )

    response.raise_for_status()

    print("metadata update completed")



with DAG(
    dag_id="status_updater",
    default_args=default_args,
    description="Runs status update through the backend API",
    schedule="@daily",
    catchup=False,
) as status_dag:

    status_update_task = PythonOperator(
        task_id="status_update_realestate_co",
        python_callable=status_updater,
        op_kwargs={
            "batch_wise": True,
            "max_batch": 1,
        },
    )

with DAG(
    dag_id="metadata_updater",
    default_args=default_args,
    description="Runs metadata update through the backend API",
    schedule="0 0 */3 * *",
    catchup=False,
) as metadata_dag:

    metadata_update_task = PythonOperator(
        task_id="metadata_update_realestate_co",
        python_callable=metadata_updater,
        op_kwargs={
            "batch_wise": True,
            "max_batch": 1,
        },
    )