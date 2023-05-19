from geojson import FeatureCollection

from db.connection import db


def get_all():
    stops = db.transit.find()
    return FeatureCollection(list(stops))
