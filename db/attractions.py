from geojson import FeatureCollection

from db.connection import db


def get_all():
    attractions = db.attractions.find()
    return FeatureCollection(list(attractions))
