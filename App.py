import folium
import streamlit as st
from folium.plugins import Draw, MousePosition
from geojson import Feature, FeatureCollection, LineString
from streamlit_folium import st_folium

import db
import plot_geojson

st.set_page_config(layout="wide")

def get_attraction_name(attraction):
    properties = attraction['properties']
    return properties.get('name')# or properties.get('scen_lm_na') or properties.get('area_name') or properties.get('lpc_name')

def get_stop_extended_name(stop):
    properties = stop['properties']
    return f"{properties.get('stop_name')} ({properties.get('stop_id')})"



st.title("Welcome to the NYC Transit App")
st.write("This app shows you NYC subway stops and nearby attractions")
# get data
subway_stops = db.subway_stops.get_all()
subway_lines = db.subway_lines.get_all()

col1, col2 = st.columns([1, 2])
with col1:
    # subway dropdown
    subway = st.selectbox("Select a subway stop", [None]+subway_stops['features'], format_func=lambda stop: get_stop_extended_name(stop) if stop else "Select a stop")
    if subway:
        nearby_attractions = db.attractions.get_near(subway['geometry']['coordinates'])
        n = len(nearby_attractions['features'])
        st.caption(f"{n} attraction{'s'[:n^1]} found near this stop.")
        with st.expander("Show attractions"):
            st.write([get_attraction_name(attraction) for attraction in nearby_attractions['features']])

    # attaction search
    name = st.text_input("Search for an attraction")
    if name:
        searched = db.attractions.get_like(name)
        n = len(searched['features'])
        st.caption(f"{n} result{'s'[:n^1]} found.")
        with st.expander("Show attractions"):
            st.write([get_attraction_name(attraction) for attraction in searched['features']])

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
        plot_geojson.radius_around_stop(subway).add_to(selected_subway_group)
        if nearby_attractions['features']:
            plot_geojson.nearby_attractions(nearby_attractions).add_to(selected_subway_group)
    
    # searched attractions layer
    if name and searched['features']:
        plot_geojson.searched_attractions(searched).add_to(m)
        
    # subway lines layer
    plot_geojson.subway_lines(subway_lines).add_to(m)
    
    # subway stops layer
    plot_geojson.subway_stops(subway_stops).add_to(m)
    
    # draw controls
    Draw(draw_options={
        'polyline': False,
        'rectangle': False,
        'polygon': False,
        'circle': False,
        'marker': { 'repeatMode': True },
        'circlemarker': False
    }).add_to(m)
    
    # layer controls
    folium.LayerControl(collapsed=True, hide_single_base=True).add_to(m)
    
    # mouse position
    MousePosition().add_to(m)
    
    # plot map
    map_data = st_folium(m, width=1000, height=500, returned_objects=['all_drawings'])
    
    def closest_stop(coords):
        near = db.subway_stops.get_near(coords)
        if near['features']:
            return near['features'][0] 
    
    def write_stop_distance(stop):
        if stop:
            st.write(f"Closest subway stop: **{get_stop_extended_name(stop)}**  \n({round(stop['distance'])} meters away)")
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
            start_stop = closest_stop(coords)
            write_stop_distance(start_stop)
        else:
            st.caption("*Put a marker on the map.*")
            
    with col2:
        st.header("End")
        if len(markers) > 1:
            coords = markers[1]['geometry']['coordinates']
            end_stop = closest_stop(coords)
            write_stop_distance(end_stop)
        else:
            st.caption("*Put a marker on the map.*")
    
    # result map
    if len(markers) > 1 and start_stop and end_stop:
        with st.expander("Show result"):
            # test route
            route = db.routes.get_route(start=start_stop['properties']['stop_id'], end=end_stop['properties']['stop_id'])
            if route:
                m = plot_geojson.result_map(markers, route, subway_stops, start_stop, end_stop)
            
            # backup map if no route could be found
            else:
                st.warning("No route could be found.")
                m = plot_geojson.backup_map(markers, start_stop, end_stop)
            
            st_folium(m, width=1000, height=500, returned_objects=[])

# TODO: refactor

# When the inputs change, the map is redrawn and the markers are removed.
# We can change this so that it updates the map seemlessly, but we lose a lot of customizability.
# Colour-coding and layers would go away.
