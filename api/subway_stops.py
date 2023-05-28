import requests
import streamlit as st


@st.cache_data
def get_all():
    r = requests.get('http://localhost:8000/subway_stops')
    r.raise_for_status()
    return r.json()

@st.cache_data
def get_near(coords, max_distance=1000, limit=10):
    r = requests.get(f'http://localhost:8000/subway_stops/near', params={
        'lon': coords[0],
        'lat': coords[1],
        'max_distance': max_distance,
        'limit': limit
    })
    r.raise_for_status()
    return r.json()
