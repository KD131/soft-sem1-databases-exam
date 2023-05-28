# Streamlit

## Table of contents

- [Setup](#setup)
- [Usage](#usage)

## Setup

Install the packages in the [`requirements.txt`](requirements.txt) file:

```shell
pip install -r requirements.txt
```

It is important that Altair get installed at that version. It currently has to be downgraded to run Streamlit.

## Usage

Run the Streamlit application with:

```shell
streamlit run App.py
```

You can select a subway stop from the dropdown. This will place an orange circle on the map in a 1000 meter radius around the stop. Any attractions found within that radius will be shown in orange.

You can search for attractions using the search field. Any matching attractions will be shown on the map in green.

To create a route, select the marker tool on the map and place two markers. Only the first two placed will count. You can move them with the edit tool and remove them with the delete tool. The order will update if you delete the original markers, i.e. the next created will be the new first two.

Once markers have been placed, it will calculate the nearest stop and generate a route to get from point A to point B. This can be shown in the resulting map further down the page.
