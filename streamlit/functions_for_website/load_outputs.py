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



def load_london_output_df():
    '''
    loads up the stored csv's for bad and good dataframes, creates a column to categorise
    them as good or bad, then merges them for output'''

    bad_df = pd.read_csv(os.path.abspath("outputs/display_bad_ldn.csv"))
    good_df = pd.read_csv(os.path.abspath("outputs/display_gd_ldn.csv"))
    all_df = pd.concat([good_df,bad_df], ignore_index=True)
    return all_df



def load_london_gdf_data(district:list):
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

    '''
    loads up the dataframes to be used for the map
    '''
    bad_df = pd.read_csv(os.path.abspath("outputs/display_bad_ldn.csv"))
    good_df = pd.read_csv(os.path.abspath("outputs/display_gd_ldn.csv"))
    carehomes = pd.read_csv(os.path.abspath("outputs/all_carehomes.csv"))


    data = good_df[good_df['district_name'].isin(district)][['lat', 'lng', 'metric']].copy()
    dataBd = bad_df[bad_df['district_name'].isin(district)][['lat', 'lng', 'metric']].copy()
    care_data = carehomes[carehomes['district_name'].isin(district)][['lat', 'lng']].copy()
    df = pd.DataFrame(data)
    df2 = pd.DataFrame(dataBd)
    df3 = pd.DataFrame(care_data)

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lng, df.lat))
    gdf2 = gpd.GeoDataFrame(df2, geometry=gpd.points_from_xy(df2.lng, df2.lat))
    gdf3 = gpd.GeoDataFrame(df3, geometry=gpd.points_from_xy(df3.lng, df3.lat))

    return gdf, gdf2, gdf3

# test = load_london_gdf_data(['Islington London Boro'])
# print(test)
