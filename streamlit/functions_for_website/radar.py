import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from gbq_functions.big_query_download import *

# district_input = ['Dorset']
def radar_chart_data(district:str):
    '''
    input single district, returns the data required for plotting a radar chart.
    DOES NOT return the actual chart
    '''
    golden_df = get_golden_df([district])
    golden_df['neg.multiplier'] = -1
    score_cols = [col for col in golden_df.columns if 'Score' in col]

    for sc in score_cols:
        golden_df[sc] = golden_df[sc] * golden_df['neg.multiplier']


    #maybe need a function for this
    good_df = pd.read_csv("../outputs/display_gd.csv")
    bad_df = pd.read_csv("../outputs/display_bad.csv")
    all_df = pd.concat([good_df, bad_df],ignore_index = True)
    output_df = all_df[all_df['district_name'] == district]

    golden_df['coord_lookup'] =  list(zip(golden_df.lat, golden_df.lng))
    output_df['coord_lookup'] =  list(zip(output_df.lat, output_df.lng))

    # dep_cols = ['Population_aged_16_59__mid_2015__excluding_prisoners_',
    #             'Older_population_aged_60_and_over__mid_2015__excluding_prisoners_',
    # "Index_of_Multiple_Deprivation__IMD__Score",
    #         'Health_Deprivation_and_Disability_Score',
    #             'Employment_Score__rate_',
    #             'Total_population__mid_2015__excluding_prisoners_',
    #             'Income_Score__rate_',
    #             'Barriers_to_Housing_and_Services_Score',
    #             'Living_Environment_Score']
    target_radius = ['_100','_250', '_500','_750', '_1000', '_1250', '_1500']
    google_options = ['national_trust','places_of_worship', 'leisure_centre','parking', 'park_', 'hospital', 'bus_station', 'train_station']
    # crime_options = ['Anti_social_behaviour', 'Public_order','Robbery', 'Other_theft', 'Other_crime']
    google_options_totals = ['national_trust_total', 'places_of_worship_total', 'leisure_centre_total','parking_total', 'park__total', 'hospital_total', 'bus_station_total', 'train_station_total']

    for feature in google_options:
        golden_df[f'{feature}_total'] = golden_df[[col for col in golden_df.columns if col.startswith(f'{feature}_')]].sum(axis=1)

    all_columns = google_options_totals + ['coord_lookup'] #removed + dep_cols
    golden_df_trimmed = golden_df[all_columns]
    combined_df = pd.merge(golden_df_trimmed, output_df, on = "coord_lookup")

    google_sum_group = combined_df.groupby("group")[google_options_totals].sum()
    # gp_num_group = combined_df.groupby("group")['gp_num'].mean()
    # dep_group = combined_df.groupby("group")[dep_cols].mean()
    # agg_df = pd.merge(google_sum_group, dep_group, left_index=True, right_index=True)
    agg_df = google_sum_group

    # all_agg_df = pd.merge(agg_df, gp_num_group, left_index=True, right_index=True)
    cols_use = agg_df.columns

    scaler = MinMaxScaler()
    scaled_df = pd.DataFrame(scaler.fit_transform(agg_df), columns = cols_use, index=agg_df.index)
    # transposed_scaled_df = pd.DataFrame(scaled_df.T, columns=agg_df.index)
    angles=np.linspace(0,2*np.pi,scaled_df.T.shape[0], endpoint=False)
    # angles=np.concatenate((angles,[angles[0]]))

    #get indexes of best, worst and middle groups
    group_list = list(output_df.group.unique())
    best = group_list[0]
    worst = group_list[-1]
    middle = group_list[len(group_list)//2]

    return scaled_df, angles, best, middle, worst
