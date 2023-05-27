import streamlit as st
import json

# test data
@st.cache_data
def get_route():
    with open("data/test.geojson") as f:
        return json.load(f)