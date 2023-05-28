import requests
import streamlit as st


@st.cache_data
def get_all():
    r = requests.get('http://localhost:8000/subway_lines')
    r.raise_for_status()
    return r.json()
