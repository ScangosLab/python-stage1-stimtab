""" tools.py
custom functions applied in filter.py
version v.1.0
DO NOT MODIFY

"""

import pandas as pd
import re

def LoadRawData(patient_id):
    if patient_id == 'PR01':
        sheet_url = 'https://docs.google.com/spreadsheets/d/1h6AoXkKo2ePL8k2CfTTGm9AlZdunyaJ1vZuU82K2gEg/edit#gid=0'
    if patient_id == 'PR03':
        sheet_url = 'https://docs.google.com/spreadsheets/d/1h6AoXkKo2ePL8k2CfTTGm9AlZdunyaJ1vZuU82K2gEg/edit#gid=582689872'
    if patient_id == 'PR04':
        sheet_url = 'https://docs.google.com/spreadsheets/d/1h6AoXkKo2ePL8k2CfTTGm9AlZdunyaJ1vZuU82K2gEg/edit#gid=932055387'
    if patient_id == 'PR05':
        sheet_url = 'https://docs.google.com/spreadsheets/d/1h6AoXkKo2ePL8k2CfTTGm9AlZdunyaJ1vZuU82K2gEg/edit#gid=1604189233'
    if patient_id == 'PR06':
        sheet_url = 'https://docs.google.com/spreadsheets/d/1h6AoXkKo2ePL8k2CfTTGm9AlZdunyaJ1vZuU82K2gEg/edit#gid=1428994273'

    csv_export_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    df = pd.read_csv(csv_export_url)

    return df


def ConfigInputData(DataFrame):
    ##Format timestamps
    DataFrame['EventStart'] = pd.to_datetime(DataFrame.EventStart, format='%Y-%m-%d %H:%M:%S.%f')
    DataFrame['EventStop'] = pd.to_datetime(DataFrame.EventStop, format='%Y-%m-%d %H:%M:%S.%f')

    ##Add date column
    DataFrame.insert(0, 'EventDate', DataFrame['EventStart'].dt.date)

    NewDataFrame = DataFrame.loc[DataFrame.EventType=='Stim'].reset_index(drop=True)
    NewDataFrame = NewDataFrame.drop(columns=DataFrame.columns.values[12:])

    lead_list = [re.split('(\d+)',x)[0] for x in NewDataFrame.PosContact]
    NewDataFrame.insert(6, 'Lead', lead_list)

    pos_n = [re.split('(\d+)',x)[1] for x in NewDataFrame.PosContact]
    neg_n = [re.split('(\d+)',x)[1] for x in NewDataFrame.NegContact]
    channel_list = NewDataFrame.Lead + pos_n + '-' + neg_n
    NewDataFrame.insert(7, 'Channels', channel_list)

    ##Add timestamps of preceding and next stim for each row
    NewDataFrame['PrevStimStop'] = pd.Series(dtype='object') #time of preceding stim
    NewDataFrame['NextStimStart'] = pd.Series(dtype='object') #time of next stim
    NewDataFrame.loc[1:, 'PrevStimStop'] = list(NewDataFrame.EventStop[:-1])
    NewDataFrame.loc[0:len(NewDataFrame)-2, 'NextStimStart'] = list(NewDataFrame.EventStart[1:])

    ##Fixing format of recently added timestamps
    NewDataFrame['PrevStimStop'] = pd.to_datetime(NewDataFrame['PrevStimStop'])
    NewDataFrame['NextStimStart'] = pd.to_datetime(NewDataFrame['NextStimStart'])

    ##Calculate difference between start of current stim and stop of previous stim, this will be pre-stim time
    NewDataFrame['DiffPrevStim'] = [x.total_seconds() for x in NewDataFrame.EventStart - NewDataFrame.PrevStimStop]
    ##Calculate difference between stop of current stim and start of next stim, this will be post-stim time
    NewDataFrame['DiffNextStim'] = [x.total_seconds() for x in NewDataFrame.NextStimStart - NewDataFrame.EventStop]

    return NewDataFrame


#GENERATE DISCRETE TRIALS: Assign filter tags
def RunFilter(DataFrame, lead_on, channels_on, frequency_on, amplitude_on, train_duration_on, time_threshold):
    if (lead_on == False) & (channels_on == False):
        filter_on = False
        print('Error: "lead_on" and "channels_on" are set to False. One must be set to True.')

    if (lead_on == True) & (channels_on == True):
        filter_on = False
        print('Error: "lead_on" and "channels_on" are set to True. Only one must be set to True.')

    if (lead_on == True) & (channels_on == False):
        filter_on = True
        tags_init = DataFrame.Lead

    if (lead_on == False) & (channels_on == True):
        filter_on = True
        tags_init = DataFrame.Channels

    if filter_on == True:
        stim_condition = list(DataFrame.StimCondition)

        if (frequency_on == True) & (amplitude_on == False) & (train_duration_on == False):
            filter_tags = tags_init \
            + '_' + pd.Series([str(int(x)) for x in DataFrame.Frequency])

        if (frequency_on == False) & (amplitude_on == True) & (train_duration_on == False):
            filter_tags = tags_init \
            + '_' + pd.Series([str(int(x)) for x in DataFrame.Amplitude])

        if (frequency_on == False) & (amplitude_on == False) & (train_duration_on == True):
            filter_tags = tags_init \
            + '_' + pd.Series([str(int(x)) for x in DataFrame.TrainDuration])

        if (frequency_on == True) & (amplitude_on == True) & (train_duration_on == False):
            filter_tags = tags_init \
            + '_' + pd.Series([str(int(x)) for x in DataFrame.Frequency]) \
            + '_' + pd.Series([str(int(x)) for x in DataFrame.Amplitude])

        if (frequency_on == False) & (amplitude_on == True) & (train_duration_on == True):
            filter_tags = tags_init \
            + '_' + pd.Series([str(int(x)) for x in DataFrame.Amplitude]) \
            + '_' + pd.Series([str(int(x)) for x in DataFrame.TrainDuration])

        if (frequency_on == True) & (amplitude_on == False) & (train_duration_on == True):
            filter_tags = tags_init \
            + '_' + pd.Series([str(int(x)) for x in DataFrame.Frequency]) \
            + '_' + pd.Series([str(int(x)) for x in DataFrame.TrainDuration])

        if (frequency_on == True) & (amplitude_on == True) & (train_duration_on == True):
            filter_tags = tags_init \
            + '_' + pd.Series([str(int(x)) for x in DataFrame.Frequency]) \
            + '_' + pd.Series([str(int(x)) for x in DataFrame.Amplitude]) \
            + '_' + pd.Series([str(int(x)) for x in DataFrame.TrainDuration])

        filter_tags_clean = []
        for i in range(len(stim_condition)):
            if 'Sham' in stim_condition[i]:
                filter_tags_clean.append(stim_condition[i])
            if 'Active' in stim_condition[i]:
                filter_tags_clean.append(filter_tags[i])

        DataFrame['FilterTags'] = filter_tags_clean

        #Filter Iteration 2
        DataFrameSubset = DataFrame.loc[DataFrame['EventCondition'].isnull()].reset_index(drop=True)

        ##Initialize list
        if DataFrameSubset['FilterTags'][0] != DataFrameSubset['FilterTags'][1]:
            break_list1 = ['single_stim']
        if (DataFrameSubset['FilterTags'][0] == DataFrameSubset['FilterTags'][1]):
            break_list1 = ['trial_start']

        for i in range(1, len(DataFrameSubset['FilterTags'])-1):

            if (DataFrameSubset['FilterTags'][i] == DataFrameSubset['FilterTags'][i-1]) \
            & (DataFrameSubset['FilterTags'][i] == DataFrameSubset['FilterTags'][i+1]):
                break_list1.append('trial_continue')

            if (DataFrameSubset['FilterTags'][i] == DataFrameSubset['FilterTags'][i-1]) \
            & (DataFrameSubset['FilterTags'][i] != DataFrameSubset['FilterTags'][i+1]):
                break_list1.append('trial_stop')

            if (DataFrameSubset['FilterTags'][i] != DataFrameSubset['FilterTags'][i-1]) \
            & (DataFrameSubset['FilterTags'][i] == DataFrameSubset['FilterTags'][i+1]):
                break_list1.append('trial_start')

            if (DataFrameSubset['FilterTags'][i] != DataFrameSubset['FilterTags'][i-1]) \
            & (DataFrameSubset['FilterTags'][i] != DataFrameSubset['FilterTags'][i+1]):
                break_list1.append('single_stim')

        ##Add last values of list
        if DataFrameSubset['FilterTags'][len(DataFrameSubset)-1] != DataFrameSubset['FilterTags'][len(DataFrameSubset)-2]:
            break_list1.append('single_stim')

        if DataFrameSubset['FilterTags'][len(DataFrameSubset)-1] == DataFrameSubset['FilterTags'][len(DataFrameSubset)-2]:
            break_list1.append('trial_stop')

        #Add column of tags
        DataFrameSubset['BreakKey'] = break_list1

        ##Splitting long trials with same filter tags
        if time_threshold != 0:
            break_list2 = break_list1.copy()
            for i in range(len(DataFrameSubset.FilterTags)):

                if (DataFrameSubset['DiffPrevStim'][i]>time_threshold) & (DataFrameSubset['DiffNextStim'][i]>time_threshold):
                    break_list2[i] = 'single_stim'

                if (i>0) & (i<len(DataFrameSubset.FilterTags)-1):
                    if (DataFrameSubset['FilterTags'][i] == DataFrameSubset['FilterTags'][i-1]) \
                    & (DataFrameSubset['FilterTags'][i] == DataFrameSubset['FilterTags'][i+1]) \
                    & (DataFrameSubset['DiffPrevStim'][i]>time_threshold) & (DataFrameSubset['DiffNextStim'][i]<=time_threshold):
                        break_list2[i] = 'trial_start'

                    if (DataFrameSubset['FilterTags'][i] == DataFrameSubset['FilterTags'][i-1]) \
                    & (DataFrameSubset['FilterTags'][i] == DataFrameSubset['FilterTags'][i+1]) \
                    & (DataFrameSubset['DiffPrevStim'][i]<=time_threshold) \
                    & (DataFrameSubset['DiffNextStim'][i]>time_threshold):
                        break_list2[i] = 'trial_stop'

                    if (DataFrameSubset['FilterTags'][i] == DataFrameSubset['FilterTags'][i-1]) \
                    & (DataFrameSubset['FilterTags'][i] != DataFrameSubset['FilterTags'][i+1]) \
                    & (DataFrameSubset['DiffPrevStim'][i]>time_threshold):
                        break_list2[i] = 'single_stim'

            DataFrameSubset['BreakKey'] = break_list2

    return DataFrameSubset

#Final csv, filter trials based on user-specified filters if any, adds pre-stim and post-stim survey info.
def ConfigOutputData(patient_id, DataFrame, total_stim_duration, pre_stim_duration, post_stim_duration):
    ##Code that actually creates table with discrete trials.
    subset_grouped = DataFrame.groupby(DataFrame.BreakKey)
    trial_start_idx = list(subset_grouped.get_group('trial_start').index.values)
    trial_stop_idx = list(subset_grouped.get_group('trial_stop').index.values)

    discrete_trials = {}

    for i in range(len(trial_start_idx)):
        df_init = DataFrame.iloc[trial_start_idx[i]:trial_stop_idx[i]+1]
        discrete_trials[i] = {'EventDate': df_init.EventDate[trial_start_idx[i]],
                              'EventStart':df_init.EventStart[trial_start_idx[i]],
                              'EventStop': df_init.EventStop[trial_stop_idx[i]],
                              'EventType': df_init.EventType[trial_start_idx[i]],
                              'EventCondition': df_init.EventCondition[trial_start_idx[i]],
                              'StimCondition': df_init.StimCondition[trial_start_idx[i]],
                              'Lead': df_init.Lead[trial_start_idx[i]],
                              'Channels': df_init.Channels[trial_start_idx[i]],
                              'PosContact': df_init.PosContact[trial_start_idx[i]],
                              'NegContact': df_init.NegContact[trial_start_idx[i]],
                              'AmplitudeRange': list(df_init.Amplitude),
                              'AmplitudeMean': df_init.Amplitude.mean(),
                              'PulseDuration': df_init.PulseDuration[trial_start_idx[i]],
                              'TrainDurationRange': list(df_init.TrainDuration),
                              'TrainDurationMean': df_init.TrainDuration.mean(),
                              'TrainNumber': len(df_init),
                              'Frequency': df_init.Frequency[trial_start_idx[i]],
                              'TotalStimDelivered': df_init.TrainDuration.sum(),
                              'PrevStimStop': df_init.PrevStimStop[trial_start_idx[i]],
                              'NextStimStart': df_init.NextStimStart[trial_stop_idx[i]],
                              'DiffPrevStim': df_init.DiffPrevStim[trial_start_idx[i]],
                              'DiffNextStim': df_init.DiffNextStim[trial_stop_idx[i]]
                             }

    NewDataFrame = pd.DataFrame(discrete_trials).T

    if (total_stim_duration==0) & (pre_stim_duration==0) & (post_stim_duration==0):
        FinalDataFrame = NewDataFrame.copy()

    if (total_stim_duration!=0) & (pre_stim_duration!=0) & (post_stim_duration!=0):
        FinalDataFrame = NewDataFrame.loc[(NewDataFrame.TotalStimDelivered>=total_stim_duration) \
                                          & (NewDataFrame.DiffPrevStim>=pre_stim_duration) \
                                          & (NewDataFrame.DiffNextStim>=post_stim_duration)].reset_index(drop=True)

    if (total_stim_duration==0) & (pre_stim_duration!=0) & (post_stim_duration!=0):
        FinalDataFrame = NewDataFrame.loc[(NewDataFrame.DiffPrevStim>=pre_stim_duration) \
                                          & (NewDataFrame.DiffNextStim>=post_stim_duration)].reset_index(drop=True)

    if (total_stim_duration!=0) & (pre_stim_duration==0) & (post_stim_duration!=0):
        FinalDataFrame = NewDataFrame.loc[(NewDataFrame.TotalStimDelivered>=total_stim_duration) \
                                          & (NewDataFrame.DiffNextStim>=post_stim_duration)].reset_index(drop=True)

    if (total_stim_duration!=0) & (pre_stim_duration!=0) & (post_stim_duration==0):
        FinalDataFrame = NewDataFrame.loc[(NewDataFrame.TotalStimDelivered>=total_stim_duration) \
                                          & (NewDataFrame.DiffPrevStim>=pre_stim_duration)].reset_index(drop=True)

    if (total_stim_duration!=0) & (pre_stim_duration==0) & (post_stim_duration==0):
        FinalDataFrame = NewDataFrame.loc[NewDataFrame.TotalStimDelivered>=total_stim_duration].reset_index(drop=True)

    if (total_stim_duration==0) & (pre_stim_duration!=0) & (post_stim_duration==0):
        FinalDataFrame = NewDataFrame.loc[NewDataFrame.DiffPrevStim>=pre_stim_duration].reset_index(drop=True)

    if (total_stim_duration==0) & (pre_stim_duration==0) & (post_stim_duration!=0):
        FinalDataFrame = NewDataFrame.loc[NewDataFrame.DiffNextStim>=post_stim_duration].reset_index(drop=True)

    ##Assign survey timestamps pre and post stim trials/block
    ##Code chooses the closest survey collected before the start of the trial and after the trial has stopped.
    master_survey = LoadRawData(patient_id).loc[LoadRawData(patient_id).EventType=='Survey'].reset_index(drop=True)
    master_survey['EventStart'] = pd.to_datetime(master_survey.EventStart)
    trial_start = FinalDataFrame.EventStart
    trial_stop = FinalDataFrame.EventStop
    survey_times = master_survey.EventStart

    pre_stim_survey = []
    post_stim_survey = []

    for i in range(len(trial_start)):
        pre_stim_survey.append(min([x for x in survey_times if x<trial_start[i]], key=lambda x: abs(x - trial_start[i])))
        post_stim_survey.append(min([x for x in survey_times if x>trial_stop[i]], key=lambda x: abs(x - trial_stop[i])))

    FinalDataFrame['PreSurveyStart'] = pre_stim_survey
    FinalDataFrame['PostSurveyStart'] = post_stim_survey

    ##Add survey scores based on timestamps
    pre_survey_df_init = pd.DataFrame(FinalDataFrame.PreSurveyStart).merge(master_survey,
                                                                           how = 'left',
                                                                           left_on = 'PreSurveyStart',
                                                                           right_on = 'EventStart')

    post_survey_df_init = pd.DataFrame(FinalDataFrame.PostSurveyStart).merge(master_survey,
                                                                             how = 'left',
                                                                             left_on = 'PostSurveyStart',
                                                                             right_on = 'EventStart')

    unused_cols = ['EventStart', 'EventStop', 'EventType', 'EventCondition', 'StimCondition', 'PosContact',
                   'NegContact', 'Amplitude', 'PulseDuration', 'TrainDuration', 'Frequency']

    pre_survey_df = pre_survey_df_init.drop(columns=unused_cols)
    post_survey_df = post_survey_df_init.drop(columns=unused_cols)

    CuratedDataFrame = pd.concat([FinalDataFrame,
                                  pre_survey_df.iloc[:, 1:].add_prefix('Pre_'),
                                  post_survey_df.iloc[:, 1:].add_prefix('Post_')],
                                 axis=1)

    return CuratedDataFrame


"""End of code

"""
