## Setup
### Packages
For streamlit install these packages:
```shell
pip install streamlit
pip install streamlit-folium
pip install "altair<5"
```

Altair currently has to be downgraded to run Streamlit.

MongoDB and GeoJSON operations might be moved to a dedicated API, but for now install these here as well.
```shell
pip install pymongo
pip install geojson
```

### Database
Restore database from dump file.

## Data

Our data came from publicly available datasets published by the city and state of New York.
- [MTA General Transit Feed Specification (GTFS) Static Data](https://data.ny.gov/Transportation/MTA-General-Transit-Feed-Specification-GTFS-Static/fgm6-ccue)
- [Places](https://data.cityofnewyork.us/Health/Places/mzbd-kucq)
- [New York City Museums](https://data.cityofnewyork.us/Recreation/New-York-City-Museums/ekax-ky3z)
- [New York City Art Galleries](https://data.cityofnewyork.us/Recreation/New-York-City-Art-Galleries/tgyc-r5jh)
- [Theaters](https://data.cityofnewyork.us/Recreation/Theaters/kdu2-865w)
- [Individual Landmark Sites](https://data.cityofnewyork.us/Housing-Development/Individual-Landmark-Sites/ts56-fkf5)
- [Scenic Landmarks](https://data.cityofnewyork.us/Housing-Development/Scenic-Landmarks/gi7d-8gt5)
- [Historic Districts](https://data.cityofnewyork.us/Housing-Development/Historic-Districts/xbvj-gfnw)

Attractions have different name fields depending on what file they came from and what type of attraction they are. This caused issues with displaying them on the map. There were a couple options for fixing this:
1. Renaming them in code.
2. Renaming them in the database.
3. Projecting them from the database with the same name.

We opted for renaming them in the database as this would also speed up search queries because we don't need an `$or` operator. 

If you restore from dump file, you don't have to do anything, but if you create the database from scratch, run these update queries one by one. Renaming the fields in the same query didn't work.

```javascript
db.attractions.updateMany({}, {
  $rename: {
    'properties.scen_lm_na': 'properties.name'
  }
})
db.attractions.updateMany({}, {
  $rename: {
    'properties.area_name': 'properties.name'
  }
})
db.attractions.updateMany({}, {
  $rename: {
    'properties.lpc_name': 'properties.name'
  }
})
```
