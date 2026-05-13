import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from ui.frontend.tabs import find_property,agent_tab

import streamlit as st

def main():

    st.title("RealEstate JP.")

    tabs = st.tabs(["Find Property","Ai Agent"])

    with tabs[0]:
        find_property.render()
    with tabs[1]:
        agent_tab.render()

if __name__ == "__main__":
    main()