import folium
from geojson import FeatureCollection


def radius_around_stop(stop):
    return folium.GeoJson(
        FeatureCollection([stop]),
        name="Selected Stop",
        tooltip=folium.GeoJsonTooltip(fields=["stop_id", "stop_name"], aliases=["ID", "Name"]),
        popup=folium.GeoJsonPopup(fields=["stop_id", "stop_name"], aliases=["ID", "Name"]),
        marker=folium.Circle(radius=1000, dash_array='10', color='orange', fill=True, fill_color='white', fill_opacity=0.4)
    )

def nearby_attractions(attractions):
    nearby_style = {
        'fill': True,
        'color': 'orange',
        'fill_color': 'orange',
        'fill_opacity': 0.8
    }
    return folium.GeoJson(
        attractions,
        style_function=lambda x: nearby_style,
        name="Nearby Attractions",
        tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=["Name"]),
        marker=folium.Circle(radius=26, **nearby_style)
    )

def searched_attractions(attractions):
    searched_style = {
        'fill': True,
        'color': 'green',
        'fill_color': 'green',
        'fill_opacity': 0.8
    }
    return folium.GeoJson(
        attractions,
        style_function=lambda x: searched_style,
        name="Search Results",
        tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=["Name"]),
        marker=folium.Circle(radius=26, **searched_style)
    )
    
def subway_lines(subway_lines):
    return folium.GeoJson(
        subway_lines,
        name="Subway Lines",
        tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["Line"]),
        popup=folium.GeoJsonPopup(fields=["name", "rt_symbol"], aliases=["Line", "RT Symbol"])
    )

def subway_stops(subway_stops):
    return folium.GeoJson(
        subway_stops,
        name="Subway Stops",
        tooltip=folium.GeoJsonTooltip(fields=["stop_id", "stop_name"], aliases=["ID", "Name"]),
        popup=folium.GeoJsonPopup(fields=["stop_id", "stop_name"], aliases=["ID", "Name"]),
        marker=folium.Circle(radius=18, fill=True, fill_opacity=0.8)
    )

def markers(markers):
    return folium.GeoJson(
        FeatureCollection(markers),
        marker=folium.Circle(radius=26, color='purple', fill=True, fill_color='purple', fill_opacity=0.9)
    )