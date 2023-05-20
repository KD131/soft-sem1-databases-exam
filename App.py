import streamlit as st
from geojson import FeatureCollection

import db

st.title("Welcome to the NYC Transit App")
st.write("This app shows you NYC subway stops and nearby attractions")
subway_stops = db.subway_stops.get_all()
attractions = db.attractions.get_all()
all = FeatureCollection(subway_stops['features'] + attractions['features'])

coords = [stop["geometry"]["coordinates"] for stop in subway_stops['features']]

subway = st.selectbox("Select a subway stop", subway_stops['features'], format_func=lambda stop: stop['properties']['name'])
nearby_attractions = db.attractions.get_near(subway['geometry']['coordinates'])
st.write(f"{len(nearby_attractions['features'])} attractions found near this stop.")

def get_name(feature):
    properties = feature['properties']
    return properties.get('name') or properties.get('scen_lm_na') or properties.get('area_name') or properties.get('lpc_name')

st.write([get_name(attraction) for attraction in nearby_attractions['features']])


name = st.text_input("Search for an attraction")
searched = db.attractions.get_like(name)
st.write(f"{len(searched['features'])} results found.")
st.write([get_name(attraction) for attraction in searched['features']])

# Unfortunately, Streamlit doesn't support interactivity in PyDeck charts yet.
# But we can use Folium instead.
