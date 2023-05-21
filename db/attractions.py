import streamlit as st
from geojson import FeatureCollection

from db.connection import db


@st.cache_data
def get_all():
    attractions = db.attractions.find({}, { "_id": 0 } )
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
    }, { "_id": 0 } )
    return FeatureCollection(list(attractions))

@st.cache_data
def get_near(coords, max_distance=1000):
    attractions = db.attractions.find({
        "geometry": {
            "$near": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": coords
                },
                "$maxDistance": max_distance
            }
        }
    }, { "_id": 0 })
    return FeatureCollection(list(attractions))
