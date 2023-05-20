import streamlit as st
from geojson import FeatureCollection

from db.connection import db


@st.cache_data
def get_all():
    attractions = db.attractions.find()
    return FeatureCollection(list(attractions))

@st.cache_data
def get_like(name, case_sensitive=False):
    options = 'i' if not case_sensitive else ''
    query = {
        "$regex": name,
        "$options": options
    }
    
    attractions = db.attractions.find({
        "$or": [
            { "properties.name": query },
            { "properties.scen_lm_na": query },
            { "properties.area_name": query },
            { "properties.lpc_name": query }
        ]
    })
    return FeatureCollection(list(attractions))