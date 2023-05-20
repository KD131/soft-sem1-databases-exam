import streamlit as st
from geojson import FeatureCollection

import db

st.title("Welcome to the NYC Transit App")
st.write("This app shows you NYC subway stops and nearby attractions")
subway_stops = db.subway_stops.get_all()
attractions = db.attractions.get_all()
all = FeatureCollection(subway_stops['features'] + attractions['features'])


coords = [stop["geometry"]["coordinates"] for stop in subway_stops['features']]

name = st.text_input("Search for an attraction")
searched = db.attractions.get_like(name)
st.write(f"{len(searched['features'])} results found.")

# Unfortunately, Streamlit doesn't support interactivity in PyDeck charts yet.
# But we can use Folium instead.
