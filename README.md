# python-stage1-stimtab
Tool that allows tabulation of stage 1 stimulation efficacy data based on user-specified criteria.

Version: v3.0

Requirements: python>=3.8, pandas.

## Overview:
Code works using 2 python files: `tools.py` and `filter.py`. Custom functions in `tools.py` will be imported and applied in `filter.py`. Be sure to open `filter.py` on an editing tool and modify the values of the user-specified inputs according to your preferences. Save your changes and on the same command line run `python filter.py`. 

In this version, discrete periods of stimulation, referred as trials from now on, are first identified using survey timestamps as bounderies. Trials where we applied stimulation using the same parameters (by default: same contacts + frequency) continue down the pipeline. Then, information from each trial is collapsed into a row that will become part of a new output table, including survey scores pre- and post-trial. As an option, you can specify 1) a minimum of total stimulation duration applied in a trial, 2) a minimum of seconds of no stimulation before a trial, and 3) a minimum of seconds of no stimulation after a trial in order to output a table that contains trials that meet the requirements.      

## User-specified variables/inputs:
Located in `filter.py`

* `OUTPUT_DIR`: string, path to directory in server where output CSV will be saved.
* `patient_id`: string, identifier of subject in presidio study (e.g. 'PR05', it won't accept 'pr05').
* `lead_on`: boolean, if set to True, trials will be accepted as long as stimulation was delivered in the same lead, regardless of contact number. Mutually exclusive with variable `channels_on`.
* `channels_on`: boolean, if set to True, trials will be accepted as long as stimulation was delivered in the same pair of contacts. Mutually exclusive with `lead_on`.
* `frequency_on`: boolean, if set to True, frequency of stimulation will be considered as a criteria for trial eligibility. Optional and can be used in addition to other booleans. 
* `amplitude_on`: boolean, if set to True, amplitude of stimulation will be considered as criteria for trial eligibility. Optional and can be used in addition to other booleans.
* `train_duration_on`: boolean, if set to True, train duration (e.g. 10s, 20s, 120s) will be considered as criteria for trial eligibility. Optional and can be used in addition to other booleans.
* `total_stim_duration`: int or float, indicates minimum total time in seconds of stimulation delivered in a trial. This is applied AFTER trials have been identified by survey bounderies. Optional and can be used if you only want to output trials in which we delivered X seconds or more of total stimulation, otherwise set to 0.
* `pre_trial_nostim_duration`: int or float, indicates minimum time in seconds of NO stimulation before delivering the first train in a trial. This is applied AFTER trials have been identified by survey bounderies. Optional and can be used if you only want to output trials that have X seconds or more of no stimulation before the trial started, otherwise set to 0.  
* `post_trial_nostim_duration`: int or float, indicates minimum time in seconds of NO stimulation after delivering the last train in a trial. This is applied AFTER trials have been identified by survey bounderies. Optional and can be used if you only want to output trials that have X seconds or more of no stimulation after the trial ended, otherwise set to 0.

     
## tools.py
Custom functions called in "filter.py":

`LoadRawData`: Loads CSV file located in Google Drive according to `patient id`. This CSV contains surveys collected and stimulation delivered during Stage 1 ordered by timestamps. Original can be found here: https://docs.google.com/spreadsheets/d/1h6AoXkKo2ePL8k2CfTTGm9AlZdunyaJ1vZuU82K2gEg/edit?gid=1604189233#gid=1604189233 

`ConfigInputData`: Adds new columns to input data with information that will be used by filter to identify and label trials/blocks.

`AssignTags`: Reads through input dataframe and tags each train of stimulation according to `lead_on` OR `channels_on`. It will include `frequency_on`, `amplitude_on` and `train_duration_on` if these are set to True. These tags will be used by the next function to initially chunk trains as part of a discrete trial. 

`Chunker`: 
   
`ConfigOutputData`: Creates output CSV file with trials/blocks that meet user-specified criteria of `total_stim_duration`, `pre_trial_nostim_duration` and `post_trial_nostim_duration`. After selecting qualifying trials/blocks, it will add the closest survey before each trial/block starts and the closest survey after each trial/block ends.  

`ConditionalOutput`:

`LoadNKData`: Load NK annotations in dataframe based on `patient_id` (it considers differences in folder naming).

`AddBoxDisconnects`: Adds a column with disconnects timestamps and a column with reconnects timestamps.

## filter.py
Code where you can specify user inputs and apply custom functions to obtain output CSV. This is the only code you need to edit and run on the terminal.

## Output CSV file:
Output file will be saved in `OUTPUT_DIR` as `{patient_id}_Stage1_FilteredEfficacyTrials_%m%d%Y_%H%M%S`.csv where `%m%d%Y_%H%M%S` indicates date and time of file creation. 

Each row represents a trial/block of stimulation that qualified the filter criteria. There are 22 columns associated with stimulation and depending on `patient_id`, there will be a variable number of columns associated with behavioral scores (surveys). 

### Columns associated with stimulation parameters applied on each trial:

* `TrialDate`: Date a trial was conducted, format = `%Y-%m-%d`.
* `TrialStart`: Start of the first train of stimulation delivered in a trial, format = `%Y-%m-%d %H:%M:%S.%f`. 
* `TrialStop`: End of the last train of stimulation delivered in a trial.
* `StimCondition`: Indicates whether a trial is active (amplitude>0) or sham (amplitude=0).
* `Lead`: Label of intracranial electrode.
* `Channels`: Pair of contacts used for stimulation.
* `PosContact`: Positive contact used for stimulation.
* `NegContact`: Negative contact used for stimulation. 
* `AmplitudeRange`: List of amplitude values (mA) programmed for each train of stimulation a the trial.
* `AmplitudeMean`: Mean amplitude value of `AmplitudeRange`. 
* `PulseDuration`: Pulse width programmed for stimulation (for all patients is 100 us)
* `TrainDurationRange`: List of durations (s) programmed for each train of stimulation in a trial.
* `TrainDurationMean`: Mean train duration of `TrainDurationRange`.
* `TrainNumber`: Number of trains of stimulation delivered in a trial. 
* `Frequency`: Frequency used for stimulation (Hz).
* `TotalStimDelivered`: Total duration in seconds of stimulation delivered in a trial (sum of `TrainDurationRange`).
* `PreTrial_NoStim_Duration`: Indicates how many seconds of NO stim were recorded before a trial started.
* `PostTrial_NoStim_Duration`: Indicates how many seconds of NO stim were recorded after a trial ended.
* `TrialKey`: If `single_train_trial`, trial has 1 train of stimulation, if `multi_train_trial`, trial has >1 train of stimulation.
* `JunctionBoxDisconnects`: If `pre_trial_nostim_duration` and `post_trial_nostim_duration` are not 0, it will indicate any disconnection of the mini junction box that happened between `TrialStart`-`pre_trial_nostim_duration` and `TrialStop`+`post_trial_nostim_duration`. If `pre_trial_nostim_duration` and `post_trial_nostim_duration` are 0, by default it will indicate any disconnection that happened between 2 min before and 2 min after the trial.
* `JunctionBoxReconnects`: If `pre_trial_nostim_duration` and `post_trial_nostim_duration` are not 0, it will indicate any reconnection of the mini junction box that happened between `TrialStart`-`pre_trial_nostim_duration` and `TrialStop`+`post_trial_nostim_duration`. If `pre_trial_nostim_duration` and `post_trial_nostim_duration` are 0, by default it will indicate any reconnection that happened between 2 min before and 2 min after the trial.

### Columns associated with surveys identified for each trial:

* `PreTrial_SurveyStart`: Closest survey (start time) detected before `TrialStart`.
* `PostTrial_SurveyStart`: Closest survey (start time) detected after `TrialStop`.
* `PreTrial_[SurveyName]`: Closest survey score detected before `TrialStart`.
* `PostTrial_[SurveyName]`: Closest survey score detected after `TrialStop`.


