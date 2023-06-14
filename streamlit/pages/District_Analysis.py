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


'''
# Location Analysis
## Analyse by Specific Districts
'''
# for key in st.session_state.keys():
#         del st.session_state[key]
# get list of the districts (for inputs)

# @st.cache_data(persist=True)
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
#get sorted list of distric names (london boros first)
master_df['start'] = master_df['District_ID'].astype(str).str[0] #gets the letter at start of dist.
master_df_filtered = master_df[master_df['start'] == "E"] #filters for english districts only
sorted_df = master_df_filtered.sort_values(by="District_ID", ascending=False) #sorts


carehomes_df = pd.read_csv(os.path.abspath("outputs/all_carehomes.csv"))
# put source files onto github, then reference

#load output dataset
all_df = load_output_df()

labeled_df = all_df.rename(columns = {"metric": "Labels"})
lats = labeled_df['lat']
longs = labeled_df['lng']
clusters = labeled_df['Labels']

# create drop down box
option = st.selectbox("Select District:",
                      list(sorted_df['District']))

#creating buttons
with st.form("district input"):
    district_input = option
    submitted = st.form_submit_button("Search District")
    if submitted:
        if 'district' not in st.session_state:
            st.session_state['district'] = 'district_input'
            st.session_state['district'] = 'dorset'
        st.session_state['district'] = district_input

st.write(st.session_state)

# With magic:
st.session_state

# @st.cache_data(persist=True)
def get_map_data(district):
    return load_gdf_data(district)

gdf, gdf2, gdf3 = load_gdf_data(st.session_state['district'])

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
st.plotly_chart(fig)





# @st.cache_data(ttl=3660)
# def get_radar_data(district):
#     return radar_chart_data(district)

# scaled_df, angles, best, middle, worst = get_radar_data(st.session_state['district'])
# fig=plt.figure(figsize=(12,12))
# ax=fig.add_subplot(polar=True)
# #basic plot
# ax.plot(angles,scaled_df.T[best], 'o--', color='g', label='best_cluster')
# #fill plot
# ax.fill(angles, scaled_df.T[best], alpha=0.25, color='g')



# ax.plot(angles,scaled_df.T[middle], 'o--', color='b', label='middle_cluster')
# #fill plot
# ax.fill(angles, scaled_df.T[middle], alpha=0.25, color='b')


# ax.plot(angles,scaled_df.T[worst], 'o--', color='r', label='worst_cluster')
# #fill plot
# ax.fill(angles, scaled_df.T[worst], alpha=0.25, color='r')


# #Add labels
# ax.set_thetagrids(angles * 180/np.pi, scaled_df.T[best].index)
# plt.grid(True)
# plt.tight_layout()
# plt.legend()
# st.pyplot(fig)



# load output datasets
# bad_df = pd.read_csv('../outputs/display_bad.csv')
# good_df = pd.read_csv('../outputs/display_gd.csv')
# data processing
# good_df['category'] = "good"
# bad_df['category'] = "bad"
# all_df = pd.concat([good_df,bad_df], ignore_index=True)

#deprecated heatmap code

        # labeled_df_filtered = labeled_df[labeled_df['district_name']==st.session_state['district']]
        # sorted_df_filtered = sorted_df[sorted_df['District']==st.session_state['district']]
        # start_lat = sorted_df_filtered.iloc[0]['Centroid_Lat']
        # start_lon = sorted_df_filtered.iloc[0]['Centroid_Lon']
        # centre_point = [start_lat, start_lon]
        # st.session_state['centre'] = centre_point
        # lats = labeled_df_filtered['lat']
        # longs = labeled_df_filtered['lng']
        # clusters = labeled_df_filtered['Labels']
        # zipped = zip(lats, longs, clusters)
        # data = np.array(list(zipped))
        # # if 'data' not in st.session_state:
        # #     st.session_state['data'] = data
        # st.session_state['data'] = data

# def plotDot(point):
#     '''input: series that contains a numeric named latitude and a numeric named longitude
#     this function creates a CircleMarker and adds it to your this_map'''
#     folium.CircleMarker(location=[point.lat, point.lng],
#                         radius=1,
#                         weight=2).add_to(mapObj)
# zoom = 12
# if 'centre' not in st.session_state:
#     st.session_state['centre'] = [51.509865,-0.118092]
#     zoom = 6
# mapObj = folium.Map(location=st.session_state['centre'], zoom_start=zoom)
