import streamlit as st
from geojson import FeatureCollection

from db.connection import db


@st.cache_data
def get_all():
    stops = db.transit.find({}, { "_id": 0 } )
    return FeatureCollection(list(stops))

@st.cache_data
def get_near(coords, max_distance=1000):
    stops = db.transit.find({
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
    return FeatureCollection(list(stops))
