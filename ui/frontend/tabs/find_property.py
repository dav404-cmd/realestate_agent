import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(ROOT))

import streamlit as st
import requests
from manage_db.query import PropertyQuery

# ___ MAKES CARDS ___
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

# ___ LOADS PREREQUISITE INFO IN SESSION ___
def load_choices(col_name: str):
    key = f"{col_name}_options"
    if key not in st.session_state:
        try:
            response = requests.get(f"http://127.0.0.1:8000/options/{col_name}").json()
            st.session_state[key] = response.get(col_name, [])
        except Exception as e:
            st.error(f"Failed to load {col_name} options: {e}")
            st.session_state[key] = []

# ___ MAIN INTERFACE ___
def render():

    # STATE INITIALIZATION FIRST
    if "search_results" not in st.session_state:
        st.session_state.search_results = []

    if "selected_property" not in st.session_state:
        st.session_state.selected_property = None

    # Load choices for querying
    load_choices("prefecture")

    # DETAIL VIEW

    if st.session_state.selected_property is not None:

        st.header("Property Details")

        detail = requests.get(
            f"http://127.0.0.1:8000/property/{st.session_state.selected_property}"
        ).json()

        ignore_detail = ["id", "source", "scraped_at"]
        prioritized_detail = [
            "prefecture", "city", "district", "available_from",
            "layout", "type", "total_floors", "unit_floors"
        ]
        main_detail = ["price_yen","url"]

        # Main info
        st.subheader("Main Info")
        for k in main_detail:
            if k in detail and detail[k] is not None:
                st.write(f"**{k.replace('_', ' ').title()}**: {detail[k]}")

        st.divider()

        # Prioritized info
        st.subheader("Key Details")
        for k in prioritized_detail:
            if k in detail and detail[k] is not None:
                st.write(f"**{k.replace('_', ' ').title()}**: {detail[k]}")

        st.divider()

        # Other info
        st.subheader("Other Details")
        for k, v in detail.items():
            if k not in ignore_detail + prioritized_detail + main_detail and v is not None:
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
        [None] + st.session_state.prefecture_options,
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


