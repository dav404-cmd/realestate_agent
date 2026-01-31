from ui.frontend.tabs import find_property

import streamlit as st

tabs = st.tabs(["Find Property","whatever"])

with tabs[0]:
    find_property.render()
