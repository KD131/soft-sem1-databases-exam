import streamlit as st
import db

st.title("Welcome to the NYC Transit App")
st.write("This app shows you NYC subway stops and nearby attractions")
subway_stops = db.subway_stops.get_all()
st.write(subway_stops)