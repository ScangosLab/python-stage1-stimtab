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
from tools import LoadRawData, ConfigInputData, AssignTags, RunFilter1, RunFilter2, ConfigOutputData, LoadNKData, AddBoxDisconnects

# User-specified inputs #
OUTPUT_DIR = '/userdata/dastudillo/patient_data/stage1'
patient_id = 'PR06'

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
tagged_df = AssignTags(input_df, lead_on, channels_on, frequency_on, amplitude_on, train_duration_on)
filter1_df = RunFilter1(tagged_df)
filter2_df = RunFilter2(filter1_df, 120) #log10(100) = 2.0 (threshold chosen upon looking the log distribution of inter-stim durations)
pre_output_df = ConfigOutputData(patient_id, filter2_df, total_stim_duration, pre_trial_nostim_duration, post_trial_nostim_duration)

## Add disconnects and reconnects in mini junction box
if (pre_trial_nostim_duration != 0) & (post_trial_nostim_duration != 0):
    output_df = AddBoxDisconnects(patient_id, pre_output_df, pre_trial_nostim_duration, post_trial_nostim_duration)
if (pre_trial_nostim_duration == 0) & (post_trial_nostim_duration == 0):
    output_df = AddBoxDisconnects(patient_id, pre_output_df, 120, 120)

save_df = output_df.drop(columns=['PrevStimStop', 'NextStimStart']).rename(columns={'EventDate':'TrialDate',
                                                                                    'EventStart':'TrialStart',
                                                                                    'EventStop':'TrialStop',
                                                                                    'DiffPrevStim':'PreTrial_NoStim_Duration',
                                                                                    'DiffNextStim':'PostTrial_NoStim_Duration',
                                                                                    'PreSurveyStart':'PreTrial_SurveyStart',
                                                                                    'PostSurveyStart':'PostTrial_SurveyStart'})

del raw_df
del input_df
del tagged_df
del filter1_df
del filter2_df
del pre_output_df
del output_df

now = datetime.datetime.now()
creation_timestamp = now.strftime('%m%d%Y_%H%M%S')
outfile_name = f'{patient_id}_Stage1_FilteredEfficacyTrials_{creation_timestamp}.csv'
save_df.to_csv(pathlib.Path(OUTPUT_DIR, outfile_name), index=False)


"""End of code

"""
