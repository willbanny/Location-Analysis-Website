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
from google.oauth2 import service_account
import plotly.express as px
import plotly.graph_objects as go

# st.cache_data.clear()

credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])

carehomes_df = pd.read_csv(os.path.abspath("outputs/all_carehomes.csv"))

#load output dataset

all_df = load_output_df()

labeled_df = all_df.rename(columns = {"metric": "Labels"})
lats = labeled_df['lat']
longs = labeled_df['lng']
clusters = labeled_df['Labels']

st.dataframe(all_df)


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
# option = st.multiselect("select/deselect London boroughs",
#                         input_list,default=['City and County of the City of London'],
#                         on_change=st.session_state['district'] = input_list)

# set up the website to show Dorset on initializing
if 'district' not in st.session_state:
    st.session_state['district'] = input_list

#creating buttons
with st.form("district input"):
    district_input = option
    submitted = st.form_submit_button("Search District")
    if submitted:
        if 'district' not in st.session_state:
            st.session_state['district'] = 'district_input'
        st.session_state['district'] = district_input


# With magic:
st.session_state
st.write(st.session_state)

# @st.cache_data(persist=True)
def get_map_data(district):
    return load_london_gdf_data(district)

gdf, gdf2, gdf3 = load_london_gdf_data(st.session_state['district'])

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

# Radar Charts

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
