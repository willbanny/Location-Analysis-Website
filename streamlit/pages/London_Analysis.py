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
from google.cloud import bigquery
from functions_for_website.load_outputs import *
from functions_for_website.radar import *
import plotly.express as px
import plotly.graph_objects as go


'''
# Location Analysis
## Analysing the 33 London Boroughs
'''



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
# create multiselect options
# multi_option = st.multiselect("select/deselect London boroughs",
#                         input_list,default=['City and County of the City of London'],
#                         on_change=st.session_state['district'] = input_list])




st.session_state['district'] = input_list

@st.cache_data(persist=True)
def get_map_data():
    return load_london_gdf_data()

gdf, gdf2, gdf3 = load_london_gdf_data()

scatter_trace = go.Scattermapbox(
    lat=gdf['lat'],
    lon=gdf['lng'],
    mode='markers',
    marker=dict(
        size=5,
        sizeref=1,
        color=gdf['metric'],
        colorscale='greens',
        opacity=0.6,
        colorbar=dict(title='Metric', x=0.8, len=0.4)
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
        colorscale='reds',
        opacity=0.6,
        colorbar=dict(title='Metric', x=1.0, len=0.4)
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

# Bar Chart?
