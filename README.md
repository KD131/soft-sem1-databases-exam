# MongoDB and Streamlit

## Table of contents

- [1. Setup](#1-setup)
  - [1.1. Packages](#11-packages)
  - [1.2. Database](#12-database)
- [2. Usage](#2-usage)
- [3. Data](#3-data)
  - [3.1. Sources](#31-sources)
  - [3.2. Imports](#32-imports)
    - [3.2.1. jq](#321-jq)
    - [3.2.2. Aggregation](#322-aggregation)
  - [3.3. Build indexes](#33-build-indexes)
  - [3.4. Updates](#34-updates)

## 1. Setup

### 1.1. Packages

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

### 1.2. Database

- Restore database from dump file.
- Alternatively build it from scratch with [instructions](#3-data)

Once we do replication and/or sharding, these commands might change, but maybe not.

The dump was created with `mongodump -d exam --archive=data/dump_archive.gzip --gzip`, so to restore it, run the following:

```shell
mongorestore --archive=dump_archive.gzip --gzip
```

This will create the `exam` database and rebuild indexes.

## 2. Usage

Run the Streamlit application with:

```shell
streamlit run App.py
```

You can select a subway stop from the dropdown. This will place an orange circle on the map in a 1000 meter radius around the stop. Any attractions found within that radius will be shown in orange.

You can search for attractions using the search field. Any matching attractions will be shown on the map in green.

To create a route, select the marker tool on the map and place two markers. Only the first two placed will count. You can move them with the edit tool and remove them with the delete tool. The order will update if you delete the original markers, i.e. the next created will be the new first two.

Once markers have been placed, it will calculate the nearest stop and generate a route to get from point A to point B. This can be shown in the resulting map further down the page.

## 3. Data

### 3.1. Sources

Our data came from publicly available datasets published by the city and state of New York.

- [MTA General Transit Feed Specification (GTFS) Static Data](https://data.ny.gov/Transportation/MTA-General-Transit-Feed-Specification-GTFS-Static/fgm6-ccue)
- [Subway Stations](https://data.cityofnewyork.us/Transportation/Subway-Stations/arq3-7z49)
- [Subway Lines](https://data.cityofnewyork.us/Transportation/Subway-Lines/3qz8-muuu)
- [Places](https://data.cityofnewyork.us/Health/Places/mzbd-kucq)
- [New York City Museums](https://data.cityofnewyork.us/Recreation/New-York-City-Museums/ekax-ky3z)
- [New York City Art Galleries](https://data.cityofnewyork.us/Recreation/New-York-City-Art-Galleries/tgyc-r5jh)
- [Theaters](https://data.cityofnewyork.us/Recreation/Theaters/kdu2-865w)
- [Individual Landmark Sites](https://data.cityofnewyork.us/Housing-Development/Individual-Landmark-Sites/ts56-fkf5)
- [Scenic Landmarks](https://data.cityofnewyork.us/Housing-Development/Scenic-Landmarks/gi7d-8gt5)
- [Historic Districts](https://data.cityofnewyork.us/Housing-Development/Historic-Districts/xbvj-gfnw)

All the data in the MongoDB database is in GeoJSON format. This allows us to perform geospatial operations and to plot the documents on a map.

The following sections concern what we did to import and setup the data in the database. If you want to recreate the database, simply [restore it](#12-database). Only if you wish to recreate the database from scratch the way we did, should you follow the following instructions yourself.

### 3.2. Imports

- [`jq`](https://stedolan.github.io/jq/) into [`mongoimport`](https://www.mongodb.com/docs/database-tools/mongoimport/)
- Alternatively, you can import the files as is and use an aggregation pipeline.

#### 3.2.1. jq

The easiest way to import the GeoJSON data is to install a tool called [jq](https://stedolan.github.io/jq/). Because the data is formatted as a `FeatureCollection` and we want each `Feature` to be a separate document, we need to extract the `features` property which is an array.

An example looks like this:

```shell
jq -c '.features' stops.geojson | mongoimport -d exam -c transit --jsonArray
```

#### 3.2.2. Aggregation

Alternatively, you can import the files as is, meaning each document is the whole of `FeatureCollection` in the file, and then use the following aggregation pipeline on each collection:

```javascript
db.transit.aggregrate([
  {
    '$unwind': {
      'path': '$features'
    }
  }, {
    '$replaceWith': '$features'
  }, {
    '$out': 'transit'
  }
])
```

### 3.3. Build indexes

We need to build geospatial indexes in order to perform geospatial operations on the collections.

```javascript
db.transit.createIndex({geometry: '2dsphere'})
db.attractions.createIndex({geometry: '2dsphere'})
```

### 3.4. Updates

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
