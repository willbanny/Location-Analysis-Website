import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium, folium_static
# from gbq_functions.big_query_download import *
from gbq_functions.params import *
import matplotlib.pyplot as plt
from google.cloud import bigquery

'''
# Location Analysis
## District Specific
'''


# get list of the districts (for inputs)
@st.cache_data
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

    client = bigquery.Client(project=GCP_PROJECT)
    query_job = client.query(query)
    result = query_job.result()
    master_districts_df = result.to_dataframe()
    return master_districts_df
master_df = get_master_district_df()
#get sorted list of distric names (london boros first)
master_df['start'] = master_df['District_ID'].astype(str).str[0] #gets the letter at start of dist.
master_df_filtered = master_df[master_df['start'] == "E"] #filters for english districts only
sorted_df = master_df_filtered.sort_values(by="District_ID", ascending=False) #sorts

option = st.selectbox("Select District:",
                      list(sorted_df['District']))

st.dataframe(sorted_df)
start_lat = sorted_df.iloc[0]['Centroid_Lat']
start_lon = sorted_df.iloc[0]['Centroid_Lon']
centre_point = [start_lat, start_lon]

with st.form("district input"):
    district_input = option
    submitted = st.form_submit_button("Search District")
    if submitted:
        # if 'district' not in st.session_state:
        #     st.session_state['district'] = district_input
        st.session_state['district'] = district_input
        labeled_df_filtered = labeled_df[labeled_df['district_name']==st.session_state['district']]
        lats = labeled_df_filtered['lat']
        longs = labeled_df_filtered['lng']
        clusters = labeled_df_filtered['Labels']
        zipped = zip(lats, longs, clusters)
        data = np.array(list(zipped))
        # if 'data' not in st.session_state:
        #     st.session_state['data'] = data
        st.session_state['data'] = data


with st.form("carehome input"):
    carehome_submit = st.form_submit_button("Add Carehomes?")
    if carehome_submit:
        carehomes_df[carehomes_df['district_name'] == st.session_state['district']].apply(plotDot, axis = 1)

HeatMap(st.session_state['data'], scale_radius=True, radius=30).add_to(mapObj)
folium_static(mapObj, width = 725)
