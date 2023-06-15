import streamlit as st
import pandas as pd
import numpy as np
import folium
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


for key in st.session_state.keys():
        del st.session_state[key]

'''
# Location Analysis
## District Specific
'''
# for key in st.session_state.keys():
#         del st.session_state[key]
# get list of the districts (for inputs)

credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])


all_df = load_output_df()

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
master_df = master_df[master_df['start'] == "E"] #filters for english districts only
master_df = master_df.sort_values(by="District_ID", ascending=False) #sorts


# create drop down box
option = st.selectbox("Select District:",
                      list(master_df['District']))

# set up the website to show Dorset on initializing
if 'district' not in st.session_state:
    st.session_state['district'] = 'Adur District'

#creating buttons
with st.form("district input"):
    district_input = option
    submitted = st.form_submit_button("Search District")
    if submitted:
        if 'district' not in st.session_state:
            st.session_state['district'] = 'Adur District'
        st.session_state['district'] = district_input

# #creating buttons
# with st.form("district input"):
#     district_input = option
#     submitted = st.form_submit_button("Search District")
#     if submitted:
#         # if 'district' not in st.session_state:
#         #     st.session_state['district'] = district_input
#         st.session_state['district'] = district_input
#         labeled_df_filtered = labeled_df[labeled_df['district_name']==st.session_state['district']]
#         sorted_df_filtered = sorted_df[sorted_df['District']==st.session_state['district']]
#         start_lat = sorted_df_filtered.iloc[0]['Centroid_Lat']
#         start_lon = sorted_df_filtered.iloc[0]['Centroid_Lon']
#         centre_point = [start_lat, start_lon]
#         st.session_state['centre'] = centre_point
#         lats = np.array(labeled_df_filtered['lat'])
#         longs = np.array(labeled_df_filtered['lng'])
#         lat_step = max(n2 - n1 for n1, n2 in zip(sorted(set(lats)), sorted(set(lats))[1:]))
#         st.session_state['lat_step'] = lat_step

#         long_step = max(n2 - n1 for n1, n2 in zip(sorted(set(longs)), sorted(set(longs))[1:]))
#         st.session_state['long_step'] = long_step

#         clusters = np.array(labeled_df_filtered['Labels'])
#         zipped = zip(lats, longs, clusters)
#         data = np.array(list(zipped))
#         # if 'data' not in st.session_state:
#         #     st.session_state['data'] = data
#         st.session_state['data'] = data

@st.cache_data
def create_map(district):
    @st.cache_data  # :point_left: Add the caching decorator
    def load_data(csv):
        df = pd.read_csv(csv)
        return df

    df = load_data('../outputs/display_gd.csv')
    golden_df = df[df['district_name'] == district]
    golden_df = golden_df.drop_duplicates(['lat', 'lng'])
    golden_df['id'] = golden_df.index

    mapObj = folium.Map(location=[51.509865,-0.118092], zoom_start=10, prefer_canvas=True)

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
        fill_color='YlGn',
        fill_opacity=0.6,
        line_opacity=0,
        key_on='feature.id',
        bins=5
    ).add_to(mapObj)

    folium_static(mapObj, width = 725)


create_map('Cambridge District (B)')


# golden_df = all_df[all_df['district_name'] == st.session_state['district']]
# golden_df = golden_df.drop_duplicates(['lat', 'lng'])
# golden_df['id'] = golden_df.index
# mapObj = folium.Map(location=[51.509865,-0.118092], zoom_start=10, prefer_canvas=True)

# lats = np.array( golden_df['lat'] )
# longs = np.array( golden_df['lng'] )

# # set up the grid
# lat_step = max(n2 - n1 for n1, n2 in zip(sorted(set(lats)), sorted(set(lats))[1:]))
# long_step = max(n2 - n1 for n1, n2 in zip(sorted(set(longs)), sorted(set(longs))[1:]))


# my_geo_json = {
#       "type": "FeatureCollection",
#       "features": []}


# for i in range(len(lats)):
#     my_geo_json['features'].append(
#         {
#           "type": "Feature",
#           "properties": {},
#           "geometry": {
#             "type": "Polygon",
#             "coordinates": [[
#                 [longs[i] - long_step/2, lats[i] - lat_step/2],
#                 [longs[i] - long_step/2, lats[i] + lat_step/2],
#                 [longs[i] + long_step/2, lats[i] + lat_step/2],
#                 [longs[i] + long_step/2, lats[i] - lat_step/2],
#                 [longs[i] - long_step/2, lats[i] - lat_step/2],
#               ]]},
#           "id": int(golden_df['id'].values[i])
#         }
#     )


#     folium.Choropleth(
#     geo_data=my_geo_json,
#     data=golden_df,
#     columns = ['id','metric'],
#     fill_color='YlGn',
#     fill_opacity=0.5,
#     line_opacity=0,
#     key_on='feature.id',
#     bins=5
# ).add_to(mapObj)

# folium_static(mapObj, width = 725)










# def plotDot(point):
#     '''input: series that contains a numeric named latitude and a numeric named longitude
#     this function creates a CircleMarker and adds it to your this_map'''
#     folium.CircleMarker(location=[point.lat, point.lng],
#                         radius=1,
#                         weight=2).add_to(mapObj)


# def geo_json(lat, long, cluster, lat_step, long_step):
#     cmap = mpl.cm.viridis
#     return {
#       "type": "FeatureCollection",
#       "features": [
#         {
#           "type": "Feature",
#           "properties": {
#             'color': 'white',
#             'opacity': '0',
#             'weight': 1,
#             'fillColor': mpl.colors.to_hex(cmap(cluster*( 255//max(clusters) ) ) ),
#             'fillOpacity': 0.5,
#           },
#           "geometry": {
#             "type": "Polygon",
#             "coordinates": [[
#                 [long - long_step/2, lat - lat_step/2],
#                 [long - long_step/2, lat + lat_step/2],
#                 [long + long_step/2, lat + lat_step/2],
#                 [long + long_step/2, lat - lat_step/2],
#                 [long - long_step/2, lat - lat_step/2],
#               ]]}}]}

# # ...with squares...

# if 'lat_step' not in st.session_state:
#     st.session_state['lat_step'] = 0.002
# if 'long_step' not in st.session_state:
#     st.session_state['long_step'] = 0.002
# def apply_squares():
#     for i in np.arange(len(clusters)):
#         folium.GeoJson(geo_json(lats[i], longs[i], clusters[i], st.session_state['lat_step'], st.session_state['long_step'] ),
#                     lambda x: x['properties']).add_to(mapObj)
# apply_squares()

# zoom = 12
# if 'centre' not in st.session_state:
#     st.session_state['centre'] = [51.509865,-0.118092]
#     zoom = 6
# mapObj = folium.Map(location=st.session_state['centre'], zoom_start=zoom)

# with st.form("carehome input"):
#     carehome_submit = st.form_submit_button("Add Carehomes?")
#     if carehome_submit:
#         carehomes_df[carehomes_df['district_name'] == st.session_state['district']].apply(plotDot, axis = 1)



# if 'data' in st.session_state:
#     HeatMap(st.session_state['data'], scale_radius=True, radius=30).add_to(mapObj)
# folium_static(mapObj, width = 725)
