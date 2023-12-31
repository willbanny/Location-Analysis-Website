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
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="LocA", layout="wide", initial_sidebar_state="auto", menu_items=None)

for key in st.session_state.keys():
        del st.session_state[key]

st.markdown("<h1 style='text-align: center; color: black;'>LocA</h1>", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; color: black;'>London Borough Analysis </h2>", unsafe_allow_html=True)

# setting default input list of all boroughs
input_list = ['Barking and Dagenham London Boro',
 'Barnet London Boro',
 'Bexley London Boro',
 'Brent London Boro',
 'Bromley London Boro',
 'Camden London Boro',
 'City and County of the City of London',
 'City of Westminster London Boro',
 'Croydon London Boro',
 'Ealing London Boro',
 'Enfield London Boro',
 'Greenwich London Boro',
 'Hackney London Boro',
 'Hammersmith and Fulham London Boro',
 'Haringey London Boro',
 'Harrow London Boro',
 'Havering London Boro',
 'Hillingdon London Boro',
 'Hounslow London Boro',
 'Islington London Boro',
 'Kensington and Chelsea London Boro',
 'Kingston upon Thames London Boro',
 'Lambeth London Boro',
 'Lewisham London Boro',
 'Merton London Boro',
 'Newham London Boro',
 'Redbridge London Boro',
 'Richmond upon Thames London Boro',
 'Southwark London Boro',
 'Sutton London Boro',
 'Tower Hamlets London Boro',
 'Waltham Forest London Boro',
 'Wandsworth London Boro']

if 'district' not in st.session_state:
    st.session_state['district'] = input_list

if len(st.session_state['district']) == 0:
    st.session_state['district'] = input_list

#creating multi select side bar tool
selected_options = st.sidebar.multiselect("select/deselect boroughs - then click submit",
input_list)

selected_list = []
for option in selected_options:
    selected_list.append(option)

submitted = st.sidebar.button('Submit!')
if submitted:
    st.session_state['district'] = selected_list
else:
    if 'district' not in st.session_state:
        st.session_state['district'] = input_list


# getting map data and cacheing it
@st.cache_data(persist=True)
def get_map_data(district):
    return load_london_gdf_data(district)

gdf, gdf2, gdf3 = load_london_gdf_data(list(st.session_state['district']))

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
    mapbox_center={'lat': 51.52 , 'lon': -0.12},
    margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
)

fig = go.Figure(data=[scatter_trace, scatter_trace_bd, care_scat], layout=layout)
st.plotly_chart(fig, use_container_width=True)
