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
option = st.multiselect("select/deselect London boroughs",
                        input_list)


# With magic:
st.session_state
