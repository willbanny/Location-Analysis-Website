import pandas as pd
import os

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
