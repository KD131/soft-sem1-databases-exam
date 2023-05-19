import streamlit as st
from geojson import FeatureCollection

from db.connection import db


@st.cache_data
def get_all():
    attractions = db.attractions.find()
    return FeatureCollection(list(attractions))
