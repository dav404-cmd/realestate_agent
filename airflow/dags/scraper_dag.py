from airflow.sdk import DAG
from airflow.operators.python import PythonOperator

from datetime import timedelta

import requests

default_args = {
    'owner': 'admin',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def scrape_listing(max_page: int, building_type=None):
    print(
        f"Starting scraper: max_page={max_page}, type={building_type}"
    )

    payload = {
        "building_type": building_type,
        "max_page": max_page,
    }

    response = requests.post(
        "http://backend:8000/scraper/scrape_listing_af",
        json=payload,
        timeout=600,
    )

    response.raise_for_status()

    print("Scraper request accepted")



with DAG(
    dag_id="scraper",
    default_args=default_args,
    description="Runs scraper through the backend API",
    schedule="@daily",
    catchup=False,
) as dag:

    scrape_task = PythonOperator(
        task_id="scrape_realestate_co",
        python_callable=scrape_listing,
        op_kwargs={
            "max_page": 5,
            "building_type": None,
        },
    )