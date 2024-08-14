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
from tools import LoadRawData, ConfigInputData, RunFilter, ConfigOutputData, LoadNKData, AddBoxDisconnects

# User-specified inputs #
OUTPUT_DIR = '/userdata/dastudillo/patient_data/stage1/PR05'
patient_id = 'PR06'

## MUTUALLY EXCLUSIVE: choose one as True
lead_on = False
channels_on = True

## OPTIONAL: Edit what other stim parameter you want to use as criteria, you can choose more than one
## set to False or 0 when it corresponds if you don't want to include certain criteria for filtering/tabulating data
frequency_on = True
amplitude_on = False
train_duration_on = False

time_threshold = 0 #seconds
total_stim_duration = 0 #seconds
pre_stim_duration = 0 #seconds
post_stim_duration = 0 #seconds

# DO NOT MODIFY AFTER THIS LINE!!
# Start of actual CODE # 
raw_df = LoadRawData(patient_id)
input_df = ConfigInputData(raw_df)
tagged_df = RunFilter(input_df, lead_on, channels_on, frequency_on, amplitude_on, train_duration_on, time_threshold)
pre_output_df = ConfigOutputData(patient_id, tagged_df, total_stim_duration, pre_stim_duration, post_stim_duration)
output_df = pre_output_df.drop(columns=['EventType', 'EventCondition'])
## Add disconnects and reconnects in mini junction box
final_df = AddBoxDisconnects(patient_id, output_df)

del raw_df
del input_df
del pre_output_df
del output_df

now = datetime.datetime.now()
creation_timestamp = now.strftime('%m%d%Y_%H%M%S')
outfile_name = f'{patient_id}_Stage1_FilteredEfficacyTrials_{creation_timestamp}.csv'
final_df.to_csv(pathlib.Path(OUTPUT_DIR, outfile_name), index=False)


"""End of code

"""
