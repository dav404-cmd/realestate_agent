import sys
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(ROOT))

import streamlit as st
import requests
from manage_db.query import PropertyQuery

def property_card(p):
    with st.container(border=True):
        cols = st.columns([3, 1])

        # LEFT SIDE (main info)
        with cols[0]:
            st.subheader(f"{p['type'] if p['type'] else 'Type unspecified'} • {p['layout'] if p['layout'] else 'Layout unspecified'}")

            location = f"{p['district']}, {p['city']}, {p['prefecture']}"
            st.write(location)

            st.write(f"Price: {p['price_yen']:,} yen")
            st.write(f"📐 {p['size']} m² | Land: {p['land_area']} m²")
            st.write(f"Built: {p['construction_completed']}")
            st.write(f"🚉 {p['nearest_station']}")
            st.write(f"Prefecture : {p['prefecture']}")

            if p["occupancy"]:
                st.write(f"Status: {p['occupancy']}")

        # RIGHT SIDE (action)
        with cols[1]:
            if st.button("View", key=f"view_{p['id']}"):
                st.session_state.selected_property = p["id"]


def render():

    # STATE INITIALIZATION FIRST
    if "search_results" not in st.session_state:
        st.session_state.search_results = []

    if "selected_property" not in st.session_state:
        st.session_state.selected_property = None


    # DETAIL VIEW
    #todo: format the details ignoring unwanted info
    if st.session_state.selected_property is not None:

        st.header("Property Details")

        detail = requests.get(
            f"http://127.0.0.1:8000/property/{st.session_state.selected_property}"
        ).json()

        for k, v in detail.items():
            if v is not None:
                st.write(f"**{k.replace('_', ' ').title()}**: {v}")

        if st.button("Back"):
            st.session_state.selected_property = None
            st.rerun()

        return  # stop rendering search UI


    # SEARCH UI
    st.header("Properties.")

    min_price = st.number_input("Min price (yen)", min_value=0)
    max_price = st.number_input("Max price (yen)", min_value=0)

    prefecture = st.selectbox(
        "Prefecture",
        (None, "Tokyo", "Kanagawa"),
        key="prefecture_find"
    )

    query = PropertyQuery(
        min_price=min_price if min_price > 0 else None,
        max_price=max_price if max_price > 0 else None,
        prefecture=prefecture if prefecture else None
    )

    if st.button("Find", key="search_find"):
        payload = query.model_dump(exclude_none=True)

        response = requests.post(
            "http://127.0.0.1:8000/search",
            json=payload
        )

        try:
            st.session_state.search_results = response.json()
        except Exception:
            st.error("Invalid response from server.")
            return


    # RENDER
    if st.session_state.search_results:
        for p in st.session_state.search_results:
            property_card(p)
    else:
        st.info("No property found.")


