""" filter.py
tool to create table with discrete stim trials/block metadata. output in csv format.
version v2.0

"""

# Import standard libraries #
import pandas as pd
import numpy as np
import datetime
import re
import pathlib 

# Import custom functions #
from tools import LoadRawData, ConfigInputData, Chunker, ConfigOutputData, ConditionalOutput, LoadNKData, AddBoxDisconnects

# User-specified inputs #
OUTPUT_DIR = '/userdata/dastudillo/patient_data/stage1'
patient_id = 'PR05'

## MUTUALLY EXCLUSIVE: choose one as True
lead_on = False
channels_on = True

## OPTIONAL: Edit what other stim parameter you want to use as criteria, you can choose more than one
## set to False or 0 when it corresponds if you don't want to include certain criteria for filtering/tabulating data
frequency_on = True
amplitude_on = False
train_duration_on = False

total_stim_duration = 0 #seconds
pre_trial_nostim_duration = 0 #seconds
post_trial_nostim_duration = 0 #seconds

# DO NOT MODIFY AFTER THIS LINE!!
# Start of actual CODE # 
raw_df = LoadRawData(patient_id)
input_df = ConfigInputData(raw_df)
chunked_df = Chunker(input_df, lead_on, channels_on, frequency_on, amplitude_on, train_duration_on)
curated_df = ConfigOutputData(chunked_df)

if (total_stim_duration!=0) & (pre_trial_nostim_duration!=0) & (post_trial_nostim_duration!=0):
    conditional_df = ConditionalOutput(curated_df, total_stim_duration, pre_trial_nostim_duration, post_trial_nostim_duration)
    output_df = AddBoxDisconnects(patient_id, conditional_df, pre_trial_nostim_duration, post_trial_nostim_duration)

if (total_stim_duration==0) & (pre_trial_nostim_duration==0) & (post_trial_nostim_duration==0):
    output_df = curated_df.copy()

del raw_df
del input_df
del chunked_df
del curated_df

now = datetime.datetime.now()
creation_timestamp = now.strftime('%m%d%Y_%H%M%S')
outfile_name = f'{patient_id}_Stage1_FilteredEfficacyTrials_{creation_timestamp}.csv'
output_df.to_csv(pathlib.Path(OUTPUT_DIR, outfile_name), index=False)


"""End of code

"""
