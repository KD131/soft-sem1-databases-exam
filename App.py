import folium
import streamlit as st
from geojson import FeatureCollection
from streamlit_folium import st_folium

import db

st.set_page_config(layout="wide")

st.title("Welcome to the NYC Transit App")
st.write("This app shows you NYC subway stops and nearby attractions")
# get data
subway_stops = db.subway_stops.get_all()
for stop in subway_stops['features']:
    del stop['_id']
attractions = db.attractions.get_all()
all = FeatureCollection(subway_stops['features'] + attractions['features'])

col1, col2 = st.columns(2)

with col1:
    # subway dropdown
    subway = st.selectbox("Select a subway stop", subway_stops['features'], format_func=lambda stop: stop['properties']['name'])
    nearby_attractions = db.attractions.get_near(subway['geometry']['coordinates'])
    st.write(f"{len(nearby_attractions['features'])} attractions found near this stop.")
    def get_name(feature):
        properties = feature['properties']
        return properties.get('name') or properties.get('scen_lm_na') or properties.get('area_name') or properties.get('lpc_name')

    with st.expander("Show attractions"):
        st.write([get_name(attraction) for attraction in nearby_attractions['features']])

    # attaction search
    name = st.text_input("Search for an attraction")
    searched = db.attractions.get_like(name)
    st.write(f"{len(searched['features'])} results found.")
    with st.expander("Show attractions"):
        st.write([get_name(attraction) for attraction in searched['features']])

with col2:
    # create map
    coords = [stop["geometry"]["coordinates"] for stop in subway_stops['features']]
    lons, lats = zip(*coords)
    m = folium.Map()
    m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])
    folium.GeoJson(subway_stops,
                   name="Subway Stops",
                   tooltip=folium.GeoJsonTooltip(fields=["name", "line"], aliases=["Stop Name", "Line"]),
                   popup=folium.GeoJsonPopup(fields=["name", "line", "notes"], aliases=["Stop Name", "Line", "Notes"]),
                   marker=folium.Circle(radius=20, fill=True, fill_opacity=0.8)
                   ).add_to(m)
    map_data = st_folium(m, width=1200, height=800, returned_objects=[])

