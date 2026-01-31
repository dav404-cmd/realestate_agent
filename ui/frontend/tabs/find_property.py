import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(ROOT))

import streamlit as st
import requests
from manage_db.query import PropertyQuery

def render():
    st.header("Properties.")

    min_price = st.number_input("Min price (yen)", min_value=0)
    max_price = st.number_input("Max price (yen)", min_value=0)

    min_price = min_price if min_price > 0 else None
    max_price = max_price if max_price > 0 else None

    prefecture = st.selectbox("Prefecture",("Tokyo","Kanagawa"),key="prefecture_find")

    query = PropertyQuery(
        min_price= min_price if min_price else None,
        max_price= max_price if max_price else None,
        prefecture= prefecture if prefecture else None
    )

    if st.button("Find",key="search_find"):
        payload = query.model_dump(exclude_none=True)

        response = requests.post(
            "http://127.0.0.1:8000/search",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        st.json(response.text)