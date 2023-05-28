import folium
from geojson import FeatureCollection, Feature, LineString


# TODO: rename functions to avoid name conflicts
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

def markers(_markers):
    return folium.GeoJson(
        FeatureCollection(_markers),
        marker=folium.Circle(radius=26, color='purple', fill=True, fill_color='purple', fill_opacity=0.9)
    )
    
def route(_route):
    return folium.GeoJson(
        _route,
        name="Route",
        tooltip=folium.GeoJsonTooltip(fields=['departure', 'arrival'], aliases=['Departure', 'Arrival']),
        popup=folium.GeoJsonPopup(fields=['departure', 'arrival'], aliases=['Departure', 'Arrival'])
    )

def walk_to_markers(_markers, start_stop, end_stop):
    return folium.GeoJson(
        FeatureCollection([
            Feature(geometry=LineString([start_stop['geometry']['coordinates'], _markers[0]['geometry']['coordinates']])),
            Feature(geometry=LineString([end_stop['geometry']['coordinates'], _markers[1]['geometry']['coordinates']]))
        ]),
        style_function=lambda x: {
            'color': '#0e1117',
            'dashArray': '10'
        }
    )

def sw_ne_corners(coords):
    lons, lats = zip(*coords)
    return (min(lats), min(lons)), (max(lats), max(lons))

def result_map(_markers, _route, all_stops, start_stop, end_stop):
    m = folium.Map()
    
    markers(_markers).add_to(m)
    route(_route).add_to(m)
    
    # route stops
    # these could have been included in the route GeoJSON as Point Features, but then they would be styled the same as the route
    route_stop_ids = {line['properties']['start_parent'] for line in _route['features']} | {line['properties']['end_parent'] for line in _route['features']}
    route_stops = [stop for stop in all_stops['features'] if stop['properties']['stop_id'] in route_stop_ids]
    subway_stops(FeatureCollection(route_stops)).add_to(m)
    # if the direction of the route could be trusted, we wouldn't need explicit start and end stops
    walk_to_markers(_markers, start_stop, end_stop).add_to(m)
    
    coords = [marker['geometry']['coordinates'] for marker in _markers]
    m.fit_bounds(sw_ne_corners(coords))
    
    return m

def backup_map(_markers, start_stop, end_stop):
    m = folium.Map()
    
    markers(_markers).add_to(m)
    subway_stops(FeatureCollection([start_stop, end_stop])).add_to(m)
    route(
        FeatureCollection([
            Feature(
                geometry=LineString([start_stop['geometry']['coordinates'], end_stop['geometry']['coordinates']]),
                properties={'departure': '', 'arrival': ''}
            )
        ])
    ).add_to(m)
    walk_to_markers(_markers, start_stop, end_stop).add_to(m)
    
    coords = [marker['geometry']['coordinates'] for marker in _markers]
    m.fit_bounds(sw_ne_corners(coords))
    
    return m
