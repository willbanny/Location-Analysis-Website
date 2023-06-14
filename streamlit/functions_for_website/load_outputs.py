import pandas as pd
import os
import geopandas as gpd
# from shapely.geometry import Polygon, Point
# from math import cos, pi

def load_output_df():
    '''
    loads up the stored csv's for bad and good dataframes, creates a column to categorise
    them as good or bad, then merges them for output'''

    bad_df = pd.read_csv(os.path.abspath("outputs/display_bad.csv"))
    good_df = pd.read_csv(os.path.abspath("outputs/display_gd.csv"))
    good_df['category'] = "good"
    bad_df['category'] = "bad"
    all_df = pd.concat([good_df,bad_df], ignore_index=True)
    return all_df



def load_gdf_data(district:str):
    '''
    loads up the dataframes to be used for the map
    '''
    bad_df = pd.read_csv(os.path.abspath("outputs/display_bad.csv"))
    good_df = pd.read_csv(os.path.abspath("outputs/display_gd.csv"))
    carehomes = pd.read_csv(os.path.abspath("outputs/all_carehomes.csv"))


    data = good_df[good_df['district_name'].str.contains(district, regex=False)][['lat', 'lng', 'metric']].copy()
    dataBd = bad_df[bad_df['district_name'].str.contains(district, regex=False)][['lat', 'lng', 'metric']].copy()
    care_data = carehomes[carehomes['district_name'].str.contains(district, regex=False)][['lat', 'lng']].copy()

    df = pd.DataFrame(data)
    df2 = pd.DataFrame(dataBd)
    df3 = pd.DataFrame(care_data)

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lng, df.lat))
    gdf2 = gpd.GeoDataFrame(df2, geometry=gpd.points_from_xy(df2.lng, df2.lat))
    gdf3 = gpd.GeoDataFrame(df3, geometry=gpd.points_from_xy(df3.lng, df3.lat))

    return gdf, gdf2, gdf3

