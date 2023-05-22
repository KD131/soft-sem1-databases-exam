import folium
import streamlit as st
from folium.plugins import Draw, MousePosition
from geojson import FeatureCollection
from streamlit_folium import st_folium

import db

st.set_page_config(layout="wide")

def get_name(feature):
    properties = feature['properties']
    return properties.get('name')# or properties.get('scen_lm_na') or properties.get('area_name') or properties.get('lpc_name')


st.title("Welcome to the NYC Transit App")
st.write("This app shows you NYC subway stops and nearby attractions")
# get data
subway_stops = db.subway_stops.get_all()

col1, col2 = st.columns([1, 2])
with col1:
    # subway dropdown
    subway = st.selectbox("Select a subway stop", subway_stops['features'], format_func=lambda stop: stop['properties']['name'])
    # unfortunately it always selects something anyway.
    if subway:
        nearby_attractions = db.attractions.get_near(subway['geometry']['coordinates'])
        n = len(nearby_attractions['features'])
        st.caption(f"{n} attraction{'s'[:n^1]} found near this stop.")
        with st.expander("Show attractions"):
            st.write([get_name(attraction) for attraction in nearby_attractions['features']])

    # attaction search
    name = st.text_input("Search for an attraction")
    if name:
        searched = db.attractions.get_like(name)
        n = len(searched['features'])
        st.caption(f"{n} result{'s'[:n^1]} found.")
        with st.expander("Show attractions"):
            st.write([get_name(attraction) for attraction in searched['features']])

with col2:
    # create map
    coords = [stop["geometry"]["coordinates"] for stop in subway_stops['features']]
    lons, lats = zip(*coords)
    m = folium.Map()
    m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])
    
    # selected stop layer
    # this goes first so that the other features are selectable on top of it
    if subway:
        selected_subway_group = folium.FeatureGroup(name="Selected Stop").add_to(m)
        folium.GeoJson(FeatureCollection([subway]),
                       name="Selected Stop",
                       tooltip=folium.GeoJsonTooltip(fields=["name", "line"], aliases=["Stop Name", "Line"]),
                       popup=folium.GeoJsonPopup(fields=["name", "line", "notes"], aliases=["Stop Name", "Line", "Notes"]),
                       marker=folium.Circle(radius=1000, dash_array='10', color='orange', fill=True, fill_color='white', fill_opacity=0.4)
                       ).add_to(selected_subway_group)
        if nearby_attractions['features']:
            nearby_style = {
                'fill': True,
                'color': 'orange',
                'fill_color': 'orange',
                'fill_opacity': 0.8
            }
            folium.GeoJson(nearby_attractions,
                    style_function=lambda x: nearby_style,
                    name="Nearby Attractions",
                    tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=["Name"]),
                    marker=folium.Circle(radius=30, **nearby_style)
                    ).add_to(selected_subway_group)
    
    # searched attractions layer
    if name and searched['features']:
        searched_style = {
            'fill': True,
            'color': 'green',
            'fill_color': 'green',
            'fill_opacity': 0.8
        }
        folium.GeoJson(searched,
                    style_function=lambda x: searched_style,
                    name="Search Results",
                    tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=["Name"]),
                    marker=folium.Circle(radius=30, **searched_style)
                    ).add_to(m)
    
    # subway stops layer
    folium.GeoJson(subway_stops,
                   name="Subway Stops",
                   tooltip=folium.GeoJsonTooltip(fields=["name", "line"], aliases=["Stop Name", "Line"]),
                   popup=folium.GeoJsonPopup(fields=["name", "line", "notes"], aliases=["Stop Name", "Line", "Notes"]),
                   marker=folium.Circle(radius=20, fill=True, fill_opacity=0.8)
                   ).add_to(m)
    
    
    Draw(draw_options={
        'polyline': False,
        'rectangle': False,
        'polygon': False,
        'circle': False,
        'marker': { 'repeatMode': True },
        'circlemarker': False
        }).add_to(m)
    folium.LayerControl(collapsed=True, hide_single_base=True).add_to(m)
    MousePosition().add_to(m)
    map_data = st_folium(m, width=1000, height=500, returned_objects=['all_drawings'])
    
    def closest_stop(coords):
        near = db.subway_stops.get_near(coords)
        if near['features']:
            closest = near['features'][0]
            st.write(f"Closest subway stop: **{closest['properties']['name']}**  \n({round(closest['distance'])} meters away)")
        else:
            st.write("No nearby subway stops.")
    
    # start and end markers
    # first two markers but could just as well be the last two
    markers = (map_data['all_drawings'] if map_data['all_drawings'] is not None else [])[:2]
    col1, col2 = st.columns(2)
    with col1:
        st.header("Start")
        if len(markers) > 0:
            coords = markers[0]['geometry']['coordinates']
            closest_stop(coords)
        else:
            st.caption("*Put a marker on the map.*")
            
    with col2:
        st.header("End")
        if len(markers) > 1:
            coords = markers[1]['geometry']['coordinates']
            closest_stop(coords)
        else:
            st.caption("*Put a marker on the map.*")

# When the inputs change, the map is redrawn and the markers are removed.
# We can change this so that it updates the map seemlessly, but we lose a lot of customizability.
# Colour-coding and layers would go away.
