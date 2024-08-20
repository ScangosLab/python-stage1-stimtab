""" tools.py
custom functions applied in filter.py
version v3.0
DO NOT MODIFY

"""

import pandas as pd
import re
import pathlib
import os
import datetime
from datetime import timedelta

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
    NewDataFrame = DataFrame.copy()
    NewDataFrame['EventStart'] = pd.to_datetime(DataFrame.EventStart, format='%Y-%m-%d %H:%M:%S.%f')
    NewDataFrame['EventStop'] = pd.to_datetime(DataFrame.EventStop, format='%Y-%m-%d %H:%M:%S.%f')
    ##Add date column
    NewDataFrame.insert(0, 'EventDate', NewDataFrame['EventStart'].dt.date)

    StimDataFrame = NewDataFrame.loc[NewDataFrame.EventType=='Stim'].reset_index(drop=True)
    SurveysDataFrame = NewDataFrame.loc[NewDataFrame.EventType=='Survey'].reset_index(drop=True)

    del NewDataFrame
    
    lead_list = [re.split('(\d+)',x)[0] for x in StimDataFrame.PosContact]
    StimDataFrame['Lead'] = lead_list

    pos_contacts = [re.split('(\d+)',x)[1] for x in StimDataFrame.PosContact]
    neg_contacts = [re.split('(\d+)',x)[1] for x in StimDataFrame.NegContact]
    channel_list = StimDataFrame.Lead + pos_contacts + '-' + neg_contacts
    StimDataFrame['Channels'] = channel_list

    ##Add timestamps of preceding and next stim for each row
    StimDataFrame['PrevStimStop'] = pd.Series(dtype='object') #time of preceding stim
    StimDataFrame['NextStimStart'] = pd.Series(dtype='object') #time of next stim
    StimDataFrame.loc[1:, 'PrevStimStop'] = list(StimDataFrame.EventStop[:-1])
    StimDataFrame.loc[0:len(StimDataFrame)-2, 'NextStimStart'] = list(StimDataFrame.EventStart[1:])
    ##Fixing format of recently added timestamps
    StimDataFrame['PrevStimStop'] = pd.to_datetime(StimDataFrame['PrevStimStop'])
    StimDataFrame['NextStimStart'] = pd.to_datetime(StimDataFrame['NextStimStart'])
    ##Calculate difference between start of current stim and stop of previous stim, this will be pre-stim time
    StimDataFrame['PreTrial_NoStim_Duration'] = [x.total_seconds() for x in StimDataFrame.EventStart - StimDataFrame.PrevStimStop]
    ##Calculate difference between stop of current stim and start of next stim, this will be post-stim time
    StimDataFrame['PostTrial_NoStim_Duration'] = [x.total_seconds() for x in StimDataFrame.NextStimStart - StimDataFrame.EventStop]

    NewDataFrame = pd.concat([StimDataFrame, SurveysDataFrame], ignore_index=True).sort_values(by='EventStart').reset_index(drop=True)
    col6 = NewDataFrame.pop('Lead')
    col7 = NewDataFrame.pop('Channels')
    col14 = NewDataFrame.pop('PrevStimStop')
    col15 = NewDataFrame.pop('NextStimStart')
    col16 = NewDataFrame.pop('PreTrial_NoStim_Duration')
    col17 = NewDataFrame.pop('PostTrial_NoStim_Duration')

    NewDataFrame.insert(6, 'Lead', col6)
    NewDataFrame.insert(7, 'Channels', col7)
    NewDataFrame.insert(14, 'PrevStimStop', col14)
    NewDataFrame.insert(15, 'NextStimStart', col15)
    NewDataFrame.insert(16, 'PreTrial_NoStim_Duration', col16)
    NewDataFrame.insert(17, 'PostTrial_NoStim_Duration', col17)

    del StimDataFrame
    del SurveysDataFrame

    return NewDataFrame

#ASSIGN TEMPORARY TAGS TO IDENTIFY PERIODS OF STIMULATION USING SAME PARAMETERS
def AssignTags(DataFrame, lead_on, channels_on, frequency_on, amplitude_on, train_duration_on):
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
            + '_' + pd.Series([str(int(x)) for x in DataFrame.Frequency], dtype=str)

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

        NewDataFrame = DataFrame.copy()
        NewDataFrame['FilterTags'] = filter_tags_clean

    return NewDataFrame

##Chunk data using survey collection as bounderies
def Chunker(DataFrame, lead_on, channels_on, frequency_on, amplitude_on, train_duration_on):
    surveys_grouped = DataFrame.groupby(DataFrame.EventType)
    surveys_idx = list(surveys_grouped.get_group('Survey').index.values)

    ChunkedDataFrame = pd.DataFrame()

    for i in range(len(surveys_idx)-2):
        TagDataFrame = DataFrame.iloc[surveys_idx[i]:surveys_idx[i+1]+1,:].reset_index(drop=True)
        tags_n = len(list(AssignTags(TagDataFrame.loc[TagDataFrame.EventType=='Stim'].reset_index(drop=True),lead_on, channels_on, frequency_on, amplitude_on, train_duration_on).FilterTags.unique()))

        if tags_n == 1:
            TagDataFrame['TrialType'] = 'single_channel_trial'
        if tags_n > 1:
            TagDataFrame['TrialType'] = 'multi_channel_trial'
        if tags_n == 0:
            TagDataFrame['TrialType'] = 'no_stim_applied'

        ChunkedDataFrame = pd.concat([ChunkedDataFrame, TagDataFrame], ignore_index=True)

    ChunkedDataFrameClean = ChunkedDataFrame.loc[ChunkedDataFrame.TrialType=='single_channel_trial'].reset_index(drop=True)
    data_grouped = ChunkedDataFrameClean.groupby(ChunkedDataFrameClean.EventType)
    pre_trial_surveys = list(data_grouped.get_group('Survey').index.values)[0::2]
    post_trial_surveys = list(data_grouped.get_group('Survey').index.values)[1::2]
    PreTrialSurveys = ChunkedDataFrameClean.iloc[pre_trial_surveys, :].reset_index(drop=True)
    PreTrialSurveys['TrialKey'] = 'pre_trial_survey'
    PostTrialSurveys = ChunkedDataFrameClean.iloc[post_trial_surveys, :].reset_index(drop=True)
    PostTrialSurveys['TrialKey'] = 'post_trial_survey'
    StimTrials = pd.DataFrame()

    for i in range(len(pre_trial_surveys)):
        DiscreteStimTrial = ChunkedDataFrameClean.iloc[pre_trial_surveys[i]+1:post_trial_surveys[i]].reset_index(drop=True)
        trial_key = []
        for index in DiscreteStimTrial.index.values:
            if len(DiscreteStimTrial)==1:
                trial_key.append('single_train_trial')
            if (len(DiscreteStimTrial)>1) & (index==0):
                trial_key.append('multi_train_trial_start')
            if (len(DiscreteStimTrial)>1) & (index!=0) & (index!=len(DiscreteStimTrial)-1):
                trial_key.append('multi_train_trial_continue')
            if (len(DiscreteStimTrial)>1) & (index!=0) & (index==len(DiscreteStimTrial)-1):
                trial_key.append('multi_train_trial_stop')
        DiscreteStimTrial['TrialKey'] = trial_key

        StimTrials = pd.concat([StimTrials, DiscreteStimTrial], ignore_index=True)

    NewDataFrame = pd.concat([PreTrialSurveys, PostTrialSurveys, StimTrials], ignore_index=True).sort_values(by='EventStart').reset_index(drop=True).drop(columns='TrialType')

    return NewDataFrame

##CONFIGURE OUTPUT DATA WITHOUT ADDING RESTRICTIONS
def ConfigOutputData(DataFrame):
    survey_cols = ['EventStart'] + list(DataFrame.columns.values[18:-1])
    ##Set aside surveys:
    PreTrialSurveys = DataFrame.loc[DataFrame.TrialKey=='pre_trial_survey'].reset_index(drop=True).loc[:,survey_cols].rename(columns={'EventStart':'SurveyStart'}).add_prefix('PreTrial_')
    PostTrialSurveys = DataFrame.loc[DataFrame.TrialKey=='post_trial_survey'].reset_index(drop=True).loc[:,survey_cols].rename(columns={'EventStart':'SurveyStart'}).add_prefix('PostTrial_')
    
    ##Set aside single-train trials:
    SingleTrainTrials = DataFrame.loc[DataFrame.TrialKey=='single_train_trial'].reset_index(drop=True).rename(columns={'EventDate':'TrialDate', 'EventStart':'TrialStart', 'EventStop':'TrialStop'})
    SingleTrainTrials['AmplitudeRange'] = SingleTrainTrials.Amplitude
    SingleTrainTrials['AmplitudeMean'] = SingleTrainTrials.Amplitude
    SingleTrainTrials['TrainDurationRange'] = SingleTrainTrials.TrainDuration
    SingleTrainTrials['TrainDurationMean'] = SingleTrainTrials.TrainDuration
    SingleTrainTrials['TrainNumber'] = 1
    SingleTrainTrials['TotalStimDelivered'] = SingleTrainTrials.TrainDuration
    
    ##Handle multi-train trials.
    trials_grouped = DataFrame.groupby(DataFrame.TrialKey)
    trial_start_idx = list(trials_grouped.get_group('multi_train_trial_start').index.values)
    trial_stop_idx = list(trials_grouped.get_group('multi_train_trial_stop').index.values)

    MultiTrainTrials = {}

    for i in range(len(trial_start_idx)):
        MultiTrainTrial = DataFrame.iloc[trial_start_idx[i]:trial_stop_idx[i]+1]
        MultiTrainTrials[i] = {'TrialDate': MultiTrainTrial.EventDate[trial_start_idx[i]],
                              'TrialStart':MultiTrainTrial.EventStart[trial_start_idx[i]],
                              'TrialStop': MultiTrainTrial.EventStop[trial_stop_idx[i]],
                              #'EventType': df_init.EventType[trial_start_idx[i]],
                              'EventCondition': MultiTrainTrial.EventCondition[trial_start_idx[i]],
                              'StimCondition': MultiTrainTrial.StimCondition[trial_start_idx[i]],
                              'Lead': MultiTrainTrial.Lead[trial_start_idx[i]],
                              'Channels': MultiTrainTrial.Channels[trial_start_idx[i]],
                              'PosContact': MultiTrainTrial.PosContact[trial_start_idx[i]],
                              'NegContact': MultiTrainTrial.NegContact[trial_start_idx[i]],
                              'AmplitudeRange': list(MultiTrainTrial.Amplitude),
                              'AmplitudeMean': MultiTrainTrial.Amplitude.mean(),
                              'PulseDuration': MultiTrainTrial.PulseDuration[trial_start_idx[i]],
                              'TrainDurationRange': list(MultiTrainTrial.TrainDuration),
                              'TrainDurationMean': MultiTrainTrial.TrainDuration.mean(),
                              'TrainNumber': len(MultiTrainTrial),
                              'Frequency': MultiTrainTrial.Frequency[trial_start_idx[i]],
                              'TotalStimDelivered': MultiTrainTrial.TrainDuration.sum(),
                              'PrevStimStop': MultiTrainTrial.PrevStimStop[trial_start_idx[i]],
                              'NextStimStart': MultiTrainTrial.NextStimStart[trial_stop_idx[i]],
                              'PreTrial_NoStim_Duration': MultiTrainTrial.PreTrial_NoStim_Duration[trial_start_idx[i]],
                              'PostTrial_NoStim_Duration': MultiTrainTrial.PostTrial_NoStim_Duration[trial_stop_idx[i]],
                              'TrialKey': 'multi_train_trial'
                             }

    MultiTrainTrials_Clean = pd.DataFrame(MultiTrainTrials).T
    SingleTrainTrials_Clean = SingleTrainTrials.loc[:, MultiTrainTrials_Clean.columns.values]
    AllTrials = pd.concat([MultiTrainTrials_Clean, SingleTrainTrials_Clean], ignore_index=True).sort_values(by='TrialStart').reset_index(drop=True)
    PreCuratedDataFrame = pd.concat([AllTrials, PreTrialSurveys, PostTrialSurveys], axis=1)
    CuratedDataFrame = PreCuratedDataFrame.loc[PreCuratedDataFrame['EventCondition'].isnull()].reset_index(drop=True).drop(columns=['EventCondition', 'PrevStimStop', 'NextStimStart'])
                                    
    return CuratedDataFrame

##SELECT DATA BASED ON CONDITIONS OF TOTAL STIM DURATION, PRE-TRIAL NO STIM DURATION AND POST-TRIAL NO STIM DURATION.
def ConditionalOutput(DataFrame, total_stim_duration, pre_trial_nostim_duration, post_trial_nostim_duration):
    if (total_stim_duration!=0) & (pre_trial_nostim_duration!=0) & (post_trial_nostim_duration!=0):
        NewDataFrame = DataFrame.loc[(DataFrame.TotalStimDelivered>=total_stim_duration) \
        & (DataFrame.PreTrial_NoStim_Duration>=pre_trial_nostim_duration) \
        & (DataFrame.PostTrial_NoStim_Duration>=post_trial_nostim_duration)].reset_index(drop=True)

    if (total_stim_duration==0) & (pre_trial_nostim_duration!=0) & (post_trial_nostim_duration!=0):
        NewDataFrame = DataFrame.loc[(DataFrame.PreTrial_NoStim_Duration>=pre_trial_nostim_duration) \
        & (DataFrame.PostTrial_NoStim_Duration>=post_trial_nostim_duration)].reset_index(drop=True)

    if (total_stim_duration!=0) & (pre_trial_nostim_duration==0) & (post_trial_nostim_duration!=0):
        NewDataFrame = DataFrame.loc[(DataFrame.TotalStimDelivered>=total_stim_duration) \
        & (DataFrame.PostTrial_NoStim_Duration>=post_trial_nostim_duration)].reset_index(drop=True)

    if (total_stim_duration!=0) & (pre_trial_nostim_duration!=0) & (post_trial_nostim_duration==0):
        NewDataFrame = DataFrame.loc[(DataFrame.TotalStimDelivered>=total_stim_duration) \
        & (DataFrame.PreTrial_NoStim_Duration>=pre_trial_nostim_duration)].reset_index(drop=True)

    if (total_stim_duration!=0) & (pre_trial_nostim_duration==0) & (post_trial_nostim_duration==0):
        NewDataFrame = DataFrame.loc[DataFrame.TotalStimDelivered>=total_stim_duration].reset_index(drop=True)

    if (total_stim_duration==0) & (pre_trial_nostim_duration!=0) & (post_trial_nostim_duration==0):
        NewDataFrame = DataFrame.loc[DataFrame.PreTrial_NoStim_Duration>=pre_trial_nostim_duration].reset_index(drop=True)

    if (total_stim_duration==0) & (pre_trial_nostim_duration==0) & (post_trial_nostim_duration!=0):
        NewDataFrame = DataFrame.loc[DataFrame.PostTrial_NoStim_Duration>=post_trial_nostim_duration].reset_index(drop=True)

    return NewDataFrame

##custom function to load NK annotations in a clean dataframe
def LoadNKData(patient_id, FileFormat):
    main_path = pathlib.Path(f'/data_store0/presidio/nihon_kohden/', patient_id)
    if patient_id == 'PR01':
        nk_dir = 'NK_Annotations'
    if (patient_id == 'PR03') or (patient_id == 'PR05') or (patient_id == 'PR06'):
        nk_dir = 'NK_annotations'
    if patient_id == 'PR04':
        nk_dir = 'NK_annotations_2'
    nk_path = pathlib.Path(main_path, nk_dir)

    FileNames = sorted(filter(lambda x: True if FileFormat in x else False, os.listdir(nk_path)))
    FilePaths = []
    for i in range(len(FileNames)):
        FilePaths.append(pathlib.Path(nk_path, FileNames[i]))

    ##Create dataframe where each row represents a timestamped annotation saved by the NK. 
    df_IN = []
    for path in FilePaths:
        df_OUT = pd.read_csv(path,
                             delimiter='\t',
                             header=None,
                             names=['EventType', 'EventTimestamp', 'FileID'])
        df_IN.append(df_OUT)
    df_OUT = pd.concat(df_IN).reset_index(drop=True)
    df_OUT.EventTimestamp = pd.to_datetime(df_OUT.EventTimestamp, format='%Y/%m/%d %H:%M:%S %f')
    
    return df_OUT

def AddBoxDisconnects(Subject, DataFrame, pre_trial_nostim_duration, post_trial_nostim_duration):
    nk_df = LoadNKData(Subject, 'csv')
    
    window_start = [x - timedelta(seconds=pre_trial_nostim_duration) for x in list(DataFrame.TrialStart)]
    window_stop = [x + timedelta(seconds=post_trial_nostim_duration) for x in list(DataFrame.TrialStop)]

    disconnects = list(nk_df.loc[nk_df['EventType'].str.contains('Mini junction box disconnected')].EventTimestamp)
    reconnects = list(nk_df.loc[nk_df['EventType'].str.contains('Mini junction box connected')].EventTimestamp)

    junction_box_disconnects = []
    junction_box_reconnects = []
    for i in range(len(window_start)):
        junction_box_disconnects.append([x for x in disconnects if (x>window_start[i]) & (x<window_stop[i])])
        junction_box_reconnects.append([x for x in reconnects if (x>window_start[i]) & (x<window_stop[i])])

    NewDataFrame = DataFrame.copy()

    NewDataFrame.insert(21, 'JunctionBoxDisconnects', junction_box_disconnects)
    NewDataFrame.insert(22, 'JunctionBoxReconnects', junction_box_reconnects)

    return NewDataFrame

"""End of code

"""
