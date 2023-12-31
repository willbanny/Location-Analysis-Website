import streamlit as st
import pandas as pd
import numpy as np
import folium
import os
from folium.plugins import HeatMap
from streamlit_folium import st_folium, folium_static
from gbq_functions.params import *
import matplotlib.pyplot as plt
from google.cloud import bigquery
from functions_for_website.load_outputs import *
from functions_for_website.radar import *
from google.oauth2 import service_account
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="LocA", layout="wide", initial_sidebar_state="auto", menu_items=None)

for key in st.session_state.keys():
        del st.session_state[key]

credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])

st.markdown("<h1 style='text-align: center; color: black;'>LocA</h1>", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: black;'>District Analysis </h2>", unsafe_allow_html=True)

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

#get sorted list of distric names (excluding london boroughs)
master_df['start'] = master_df['District_ID'].astype(str).str[0] #gets the letter at start of dist.
master_df = master_df[master_df['start'] == "E"]
master_df = master_df[~master_df['District'].str.contains("London",regex=False)]
master_df = master_df.sort_values(by="District", ascending=True) #sorts

carehomes_df = pd.read_csv(os.path.abspath("outputs/all_carehomes.csv"))


# create drop down box
option = st.selectbox("Select District:",
                      list(master_df['District']))

# set up the website to show first option (Adur District) on initializing
if 'district' not in st.session_state:
    st.session_state['district'] = 'Adur District'


# getting map data and caching it
# @st.cache_data(persist=True)
# def get_map_data(district):
#     return load_gdf_data(district)

if st.button('Submit!'):
    st.session_state['district'] = option
gdf, gdf2, gdf3 = load_gdf_data(st.session_state['district'])


scatter_trace = go.Scattermapbox(
    lat=gdf['lat'],
    lon=gdf['lng'],
    mode='markers',
    marker=dict(
        size=5,
        sizeref=1,
        color=gdf['metric'],
        colorscale='algae',
        opacity=0.6,
        colorbar=dict(title='Good', x=0.9, len=0.4)
    ),
    hovertext=gdf['metric'],
)

scatter_trace_bd = go.Scattermapbox(
    lat=gdf2['lat'],
    lon=gdf2['lng'],
    mode='markers',
    marker=dict(
        size=5,
        sizeref=1,
        color=gdf2['metric'],
        colorscale='reds_r',
        opacity=0.6,
        colorbar=dict(title='Bad', x=1.0, len=0.4)
    ),
    hovertext=gdf2['metric'],
)

care_scat = go.Scattermapbox(
    lat=gdf3['lat'],
    lon=gdf3['lng'],
    mode='markers',
    marker=dict(
        size=5,
        sizeref=1,
        color='blue',  # Set marker color to blue for care homes
        opacity=0.9,
    ),
    hovertext='Care Homes',
)

layout = go.Layout(
    mapbox_style='carto-positron',
    mapbox_zoom=8,
    mapbox_center={'lat': gdf['lat'].mean(), 'lon': gdf['lng'].mean()},
    margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
)

fig = go.Figure(data=[scatter_trace, scatter_trace_bd, care_scat], layout=layout)
st.plotly_chart(fig, use_container_width=True)

# Radar Charts

st.markdown(f"<h2 style='text-align: center; color: black;'>Feature Analysis: {st.session_state['district']}</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: grey;'> Point closer to edge = higher prevalence of feature in the area </h4>", unsafe_allow_html=True)


@st.cache_data(ttl=3660)
def get_radar_data(district):
    return radar_chart_data(district)

scaled_df, angles, best, middle, worst = get_radar_data(st.session_state['district'])
fig=plt.figure(figsize=(12,12))
ax=fig.add_subplot(polar=True)
#basic plot
ax.plot(angles,scaled_df.T[best], 'o--', color='g', label='best_cluster')
#fill plot
ax.fill(angles, scaled_df.T[best], alpha=0.25, color='g')



ax.plot(angles,scaled_df.T[middle], 'o--', color='b', label='middle_cluster')
#fill plot
ax.fill(angles, scaled_df.T[middle], alpha=0.25, color='b')


ax.plot(angles,scaled_df.T[worst], 'o--', color='r', label='worst_cluster')
#fill plot
ax.fill(angles, scaled_df.T[worst], alpha=0.25, color='r')


#Add labels
ax.set_thetagrids(angles * 180/np.pi, scaled_df.T[best].index)
plt.grid(True)
plt.tight_layout()
plt.legend()
st.pyplot(fig)
