import folium
import streamlit as st
from folium.plugins import Draw, MousePosition
from geojson import Feature, FeatureCollection, LineString
from streamlit_folium import st_folium

import db

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
        folium.GeoJson(FeatureCollection([subway]),
                       name="Selected Stop",
                       tooltip=folium.GeoJsonTooltip(fields=["stop_id", "stop_name"], aliases=["ID", "Name"]),
                       popup=folium.GeoJsonPopup(fields=["stop_id", "stop_name"], aliases=["ID", "Name"]),
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
                    marker=folium.Circle(radius=26, **nearby_style)
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
                    marker=folium.Circle(radius=26, **searched_style)
                    ).add_to(m)
        
    # subway lines layer
    folium.GeoJson(subway_lines,
                   name="Subway Lines",
                   tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["Line"]),
                   popup=folium.GeoJsonPopup(fields=["name", "rt_symbol"], aliases=["Line", "RT Symbol"])
                   ).add_to(m)
    
    # subway stops layer
    folium.GeoJson(subway_stops,
                   name="Subway Stops",
                   tooltip=folium.GeoJsonTooltip(fields=["stop_id", "stop_name"], aliases=["ID", "Name"]),
                   popup=folium.GeoJsonPopup(fields=["stop_id", "stop_name"], aliases=["ID", "Name"]),
                   marker=folium.Circle(radius=18, fill=True, fill_opacity=0.8)
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
        # TODO: unpack coordinates before the LineStrings
        with st.expander("Show result"):
            coords = [marker['geometry']['coordinates'] for marker in markers]
            lons, lats = zip(*coords)
            m = folium.Map()
            m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])
            
            folium.GeoJson(FeatureCollection(markers),
                           marker=folium.Circle(radius=26, color='purple', fill=True, fill_color='purple', fill_opacity=0.9)
                           ).add_to(m)
            folium.GeoJson(FeatureCollection([start_stop, end_stop]),
                           marker=folium.Circle(radius=18, fill=True, fill_opacity=0.8)
                           ).add_to(m)
            
            route = db.routes.get_route()
            folium.GeoJson(route).add_to(m)
            route_stop_ids = {line['properties']['start_parent'] for line in route['features']} | {line['properties']['end_parent'] for line in route['features']}
            route_stops = [stop for stop in subway_stops['features'] if stop['properties']['stop_id'] in route_stop_ids]
            folium.GeoJson(FeatureCollection(route_stops),
                   name="Subway Stops",
                   tooltip=folium.GeoJsonTooltip(fields=["stop_id", "stop_name"], aliases=["ID", "Name"]),
                   popup=folium.GeoJsonPopup(fields=["stop_id", "stop_name"], aliases=["ID", "Name"]),
                   marker=folium.Circle(radius=18, fill=True, fill_opacity=0.8)
                   ).add_to(m)
            
            # TODO: consider multi-line. I think if you want to style them differently, they must be different features,
            # TODO: but the line between the stops could be a multi-line.
            folium.GeoJson(FeatureCollection([
                Feature(geometry=LineString([start_stop['geometry']['coordinates'], end_stop['geometry']['coordinates']])),
                Feature(geometry=LineString([start_stop['geometry']['coordinates'], markers[0]['geometry']['coordinates']])),
                Feature(geometry=LineString([end_stop['geometry']['coordinates'], markers[1]['geometry']['coordinates']]))
            ]),
                           style_function=lambda x: {
                               'color': '#0e1117',
                               'dashArray': '10'
                           }
                           ).add_to(m)
            st_folium(m, width=1000, height=500, returned_objects=[])

# TODO: refactor

# When the inputs change, the map is redrawn and the markers are removed.
# We can change this so that it updates the map seemlessly, but we lose a lot of customizability.
# Colour-coding and layers would go away.
