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
from functions_for_website.load_outputs import *


'''
# Location Analysis
## Home Page
'''

UK_mapObj = folium.Map(location = [52.56205522008627, -1.4647329224702776], zoom_start = 6)

folium_static(UK_mapObj, width = 725)

# loading dataframes
golden_df = pd.read_csv('../raw_data/golden_df_wb_tests.csv')

#load output dataset
all_df = load_output_df()

labeled_df = all_df.rename(columns = {"metric": "Labels"})

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
# outputs_df = pd.read_csv("../outputs/model_output_labels.csv")
carehomes_df = pd.read_csv("../raw_data/care_homes_by_district.csv")

# st.dataframe(outputs_df, use_container_width=True) # only displaying a dataframe

#get sorted list of distric names (london boros first)
master_df['start'] = master_df['District_ID'].astype(str).str[0]
master_df_filtered = master_df[master_df['start'] == "E"]
sorted_df = master_df_filtered.sort_values(by="District_ID", ascending=False)




option = st.selectbox("Select District:",
                      list(sorted_df['District']))



mapObj = folium.Map(location=[51.509865,-0.118092], zoom_start=12)


lats = labeled_df['lat']
longs = labeled_df['lng']
clusters = labeled_df['Labels']
zipped = zip(lats, longs, clusters)
data = np.array(list(zipped))


def plotDot(point):
    '''input: series that contains a numeric named latitude and a numeric named longitude
    this function creates a CircleMarker and adds it to your this_map'''
    folium.CircleMarker(location=[point.lat, point.lng],
                        radius=1,
                        weight=2).add_to(mapObj)

col1, col2 = st.columns(2)

if 'stage' not in st.session_state:
    st.session_state.stage = 0

def set_stage(stage):
    st.session_state.stage = stage

# # Some code https://discuss.streamlit.io/t/after-clicking-a-submit-button-create-another-submit-button-and-do-something-else-when-that-button-is-clicked/33425/7
# st.button('First Button', on_click=set_stage, args=(1,))

# if st.session_state.stage > 0:
#     # Some code
#     st.button('Second Button', on_click=set_stage, args=(2,))
#     if st.session_state.stage > 1:
#         # More code, etc
#         st.button('Third Button', on_click=set_stage, args=(3,))
#         if st.session_state.stage > 2:
#             st.write('The end')
# st.button('Reset', on_click=set_stage, args=(0,))


with col1:
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

    with col2:
        with st.form("carehome input"):
            carehome_submit = st.form_submit_button("Add Carehomes?")
            if carehome_submit:
                carehomes_df[carehomes_df['district_name'] == st.session_state['district']].apply(plotDot, axis = 1)

HeatMap(st.session_state['data'], scale_radius=True, radius=30, gradient={.6: 'blue', .92: 'lime', 1: 'red'}).add_to(mapObj)
folium_static(mapObj, width = 725)

    # carehome_submit = st.form_submit_button("Add Carehomes?")
with col1:
    with st.form("district input2"):
        district_input = option
        submitted = st.form_submit_button("Search District2")
        if submitted:
            labeled_df_filtered2 = labeled_df[labeled_df['district_name']==district_input]
            lats2 = labeled_df_filtered2['lat']
            longs2 = labeled_df_filtered2['lng']
            clusters2 = labeled_df_filtered2['Labels']


            #create colours array for heatmap
            colours = []
            cluster_list = list(clusters2)
            for val in cluster_list:
                if val <= 0.75:
                    colours.append("red")
                elif (val > 0.75) & (val <= 1.5):
                    colours.append("orange")
                else:
                    colours.append("green")

            colours_array = np.array(colours)

            zipped = zip(lats2, longs2, clusters2, colours_array)
            data2 = np.array(list(zipped))
            m3 = folium.Map(location=[51.509865,-0.118092], zoom_start=11, tiles="cartodbpositron")

            fg = folium.FeatureGroup("Heat map", show=True)
            lats_list = list(lats2)
            longs_List = list(longs2)
            for i in range(len(lats_list)):
                folium.CircleMarker(
                    location= [lats_list[i], longs_List[i]],
                    radius=1,
                    color=colours_array[i],
                    weight=2,
                    fill=True,
                    opacity=0.5,
                ).add_to(fg)

            fg.add_to(m3)

            folium.LayerControl().add_to(m3)
            folium_static(m3, width = 725)

# adding carehome points to map


# london_carehomes.apply(plotDot, axis = 1)



# labeled_df_filtered

# filtered_df = golden_df[golden_df['district_name']==district_input]


# lats = labeled_df['lat']
# longs = labeled_df['lng']
# clusters = labeled_df['Robust__Non_PCA_Crimeless_Labels']
# zipped = zip(lats, longs, clusters)
# data = np.array(list(zipped))
# HeatMap(data, scale_radius=True, radius=30).add_to(mapObj)



# fig = plt.figure(figsize=(10, 4))

# sns.scatterplot(x=outputs_df['lng'], y=outputs_df['lat'], hue=outputs_df.Robust__Non_PCA_Crimeless_Labels, palette='Set1', marker = ".")
# sns.scatterplot(x = london_carehomes["longitude"], y = london_carehomes["latitude"], c='black' ,alpha=0.3)
# plt.show()

# sns.scatterplot(x=outputs_df['lng'], y=outputs_df['lat'], hue=outputs_df.MinMax_Non_PCA_Crimeless_Labels, palette='Set1', marker = ".")
# sns.scatterplot(x = london_carehomes["longitude"], y = london_carehomes["latitude"], c='black' ,alpha=0.3)
# plt.show()
# # st.pyplot(fig)
