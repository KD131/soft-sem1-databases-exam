import streamlit as st
from geojson import FeatureCollection

from db.connection import db


@st.cache_data
def get_all():
    stops = db.transit.find()
    return FeatureCollection(list(stops))
