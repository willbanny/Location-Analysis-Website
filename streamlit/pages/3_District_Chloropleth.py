import streamlit as st
import pandas as pd
import numpy as np
import folium
import os
from folium.plugins import HeatMap
from streamlit_folium import st_folium, folium_static
# from gbq_functions.big_query_download import *
from gbq_functions.params import *
import matplotlib.pyplot as plt
import matplotlib as mpl
from google.cloud import bigquery
from google.oauth2 import service_account
import streamlit.components.v1 as components
from functions_for_website.load_outputs import *

st.set_page_config(page_title="LocA", layout="wide", initial_sidebar_state="auto", menu_items=None)

for key in st.session_state.keys():
        del st.session_state[key]

st.markdown("<h1 style='text-align: center; color: black;'>LocA</h1>", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: black;'>Alternative Mapping Technique </h2>", unsafe_allow_html=True)

credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])

@st.cache_data(persist=True)
def get_master_district_df():
    '''function that returns the full master district df.
    Dataframe contains district name (primary key), lat_lons for the center,
    lat_lons for the edges of rectangle around area, and the area of the
    rectangle in Hectares'''

    query = f"""
            SELECT {",".join(MASTER_COLUMN_NAMES_RAW)}
            FROM {GCP_PROJECT}.{BQ_DATASET}.{BQ_DISTRICT_TABLE}
            ORDER BY HECTARES DESC
        """

    client = bigquery.Client(project=GCP_PROJECT, credentials=credentials)
    query_job = client.query(query)
    result = query_job.result()
    master_districts_df = result.to_dataframe()
    return master_districts_df
master_df = get_master_district_df()
master_df['start'] = master_df['District_ID'].astype(str).str[0] #gets the letter at start of dist.
master_df = master_df[master_df['start'] == "E"]
master_df = master_df[~master_df['District'].str.contains("London",regex=False)]
master_df = master_df.sort_values(by="District", ascending=True) #sorts


# create drop down box
option = st.selectbox("Select District:",
                      list(master_df['District']))

# set up the website to show Dorset on initializing
if 'district' not in st.session_state:
    st.session_state['district'] = 'Adur District'

@st.cache_data
def create_map(district):
    @st.cache_data  # :point_left: Add the caching decorator
    def load_data(csv):
        df = pd.read_csv(csv)
        return df

    df_good = load_data(os.path.abspath("outputs/display_gd.csv"))
    df_bad = load_data(os.path.abspath("outputs/display_bad.csv"))
    df = pd.concat([df_good, df_bad],ignore_index=True)
    golden_df = df[df['district_name'] == district]
    golden_df = golden_df.drop_duplicates(['lat', 'lng'])
    golden_df['id'] = golden_df.index

    mapObj = folium.Map(location=[golden_df['lat'].mean(),golden_df['lng'].mean()], zoom_start=10, prefer_canvas=True)

    lats = np.array( golden_df['lat'] )
    longs = np.array( golden_df['lng'] )

    # set up the grid
    lat_step = max(n2 - n1 for n1, n2 in zip(sorted(set(lats)), sorted(set(lats))[1:]))
    long_step = max(n2 - n1 for n1, n2 in zip(sorted(set(longs)), sorted(set(longs))[1:]))

    my_geo_json = {
      "type": "FeatureCollection",
      "features": []}

    for i in range(len(lats)):
        my_geo_json['features'].append(
            {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [longs[i] - long_step/2, lats[i] - lat_step/2],
                    [longs[i] - long_step/2, lats[i] + lat_step/2],
                    [longs[i] + long_step/2, lats[i] + lat_step/2],
                    [longs[i] + long_step/2, lats[i] - lat_step/2],
                    [longs[i] - long_step/2, lats[i] - lat_step/2],
                ]]},
            "id": int(golden_df['id'].values[i])
            }
        )

    folium.Choropleth(
        geo_data=my_geo_json,
        data=golden_df,
        columns = ['id','metric'],
        fill_color='RdYlGn',
        fill_opacity=0.6,
        line_opacity=0,
        key_on='feature.id',
        bins=5
    ).add_to(mapObj)

    folium_static(mapObj, width = 725)

if st.button('Submit!'):
    st.session_state['district'] = option
create_map(st.session_state['district'])
