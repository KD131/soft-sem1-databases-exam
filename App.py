import pydeck as pdk
import streamlit as st

import db

st.title("Welcome to the NYC Transit App")
st.write("This app shows you NYC subway stops and nearby attractions")
subway_stops = db.subway_stops.get_all()

coords = [stop["geometry"]["coordinates"] for stop in subway_stops['features']]
init_view = pdk.data_utils.compute_view(coords)
st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=init_view,
    layers=[
        pdk.Layer(
            'GeoJsonLayer',
            subway_stops,
            get_fill_color=[255, 255, 255, 127],
            get_line_color=[255, 255, 255, 255],
            get_point_radius=50,
            pickable=True,
        )
    ]
))
# Unfortunately, Streamlit doesn't support interactivity in PyDeck charts yet.
# But we can use Folium instead.
