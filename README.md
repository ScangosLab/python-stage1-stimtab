# python-stage1-stimtab
Tool that allows tabulation of stage 1 stimulation efficacy data based on user-specified criteria.

Version: v1.0

Requirements: python>=3.8, pandas.

## Overview:
Code works using 2 python files: `tools.py` and `filter.py`. Custom functions in `tools.py` will be imported and applied in `filter.py`. Be sure to open `filter.py` on an editing tool and modify the values of the user-specified inputs according to your preferences. Save your changes and on the same command line run `python filter.py`. 

Code reads through each row of a source dataframe and identifies the start and stop of a trial/block of stimulation based on the user-specified criteria. It then curates a new dataframe with trial metadata using identifiers previously assigned by the filter.    

## User-specified variables/inputs:

* `OUTPUT_DIR`: string, path to directory in server where output CSV will be saved.
* `patient_id`: string, identifier of subject in presidio study (e.g. 'PR05', it won't accept 'pr05').
* `lead_on`: boolean, if set to True, trials/blocks will be identified by trains of stimulation delivered in the same lead, regardless of contact number. Mutually exclusive with variable `channels_on`.
* `channels_on`: boolean, if set to True, trials/blocks will be identified by trains of stimulations delivered in the same pair of contacts. For example, after 8 trains of stimulation in LVC2-3 the filter detects that the next train of stimulation is in LVC3-4. Then the filter will assign the last train in LVC2-3 as the end of an LVC2-3 trial, and the first train of LVC3-4 as the start of a new trial. Mutually exclusive with `lead_on`.
* `frequency_on`: boolean, if set to True, frequency of stimulation will be considered as a criteria for trials/blocks identification. Optional and can be used in addition to other booleans. 
* `amplitude_on`: boolean, if set to True, amplitude of stimulation will be considered as criteria for trials/blocks identification. Optional and can be used in addition to other booleans.
* `train_duration_on`: boolean, if set to True, train duration (e.g. 10s, 20s, 120s) will be considered as criteria for trials/blocks identification. Optional and can be used in addition to other booleans. 
* `time_threshold`: int or float, indicates maximum time in seconds between the end and start of trains of stimulation that have same filter parameters. 
* `total_stim_duration`: int or float, indicates minimum total time in seconds of stimulation delivered within a trial/block. This is applied AFTER trials/blocks have been identified and labeled. Optional and can be used if you only want to output trials/blocks in which we delivered X seconds or more of total stimulation, otherwise set to 0.
* `pre_stim_duration`: int or float, indicates minimum time in seconds of NO stimulation before delivering the first train in a trial/block. This is applied AFTER trials/blocks have been identified and labeled. Optional and can be used if you only want to output trials/blocks that have X seconds or more of no stimulation before the trial started, otherwise set to 0.  
* `post_stim_duration`: int or float, indicates minimum time in seconds of NO stimulation after delivering the last train in a trial/block. This is applied AFTER trials/blocks have been identified and labeled. Optional and can be used if you only want to output trials/blocks that have X seconds or more of no stimulation after the trial ended, otherwise set to 0.

     
## tools.py
Custom functions called in "filter.py":

`LoadRawData`: Loads CSV file located in Google Drive according to `patient id`. This CSV contains surveys collected and stimulation delivered during Stage 1 ordered by timestamps. Original can be found here: https://docs.google.com/spreadsheets/d/1h6AoXkKo2ePL8k2CfTTGm9AlZdunyaJ1vZuU82K2gEg/edit?gid=1604189233#gid=1604189233 

`ConfigInputData`: Adds new columns to input data with information that will be used by filter to identify and label trials/blocks.  

`RunFilter`: Reads through input dataframe and identify trials/blocks of stimulation according to `lead_on` OR `channels_on`. It will include `frequency_on`, `amplitude_on` and `train_duration_on` if these are set to True.   

`ConfigOutputData`: Creates output CSV file with trials/blocks that meet user-specified criteria of `total_stim_duration`, `pre_stim_duration` and `post_stim_duration`. After selecting qualifying trials/blocks, it will add the closest survey before each trial/block starts and the closest survey after each trial/block ends.  

## filter.py
Code where you can specify user inputs and apply custom functions to obtain output CSV. This is the only code you need to edit and run on the terminal.

## Output CSV file:
Output file will be saved in `OUTPUT_DIR` as `{patient_id}_Stage1_FilteredEfficacyTrials_%m%d%Y_%H%M%S`.csv where `%m%d%Y_%H%M%S` indicates date and time of file creation. 

Each row represents a trial/block of stimulation that qualified the filter criteria. There are 22 columns associated with stimulation and depending on `patient_id`, there will be a variable number of columns associated with behavioral scores (surveys). 

### Columns associated with stimulation parameters applied on each trial:

* `EventDate`: Date trial/block was conducted
* `EventStart`: Start of the first train of stimulation delivered within the trial. 
* `EventStop`: End of the last train of stimulation delivered within the trial.
* `EventType`: 
* `EventCondition`: Indicates type of stimulation testing conducted. For stim efficacy trials it's NaN.
* `StimCondition`: Indicates whether a trial is active (amplitude>0) or sham (amplitude=0).
* `Lead`: Label of intracranial electrode.
* `Channels`: Pair of contacts used for stimulation.
* `PosContact`: Positive contact used for stimulation.
* `NegContact`: Negative contact used for stimulation. 
* `AmplitudeRange`: List of amplitude values used for stimulation (mA).
* `AmplitudeMean`: Mean amplitude value used for stimulation (mA). 
* `PulseDuration`: Pulse width programmed for stimulation (for all patients is 100 us)
* `TrainDurationRange`: List of times programmed for train duration (seconds).
* `TrainDurationMean`: Mean train duration used for stimulation (seconds).
* `TrainNumber`: Number of trains of stimulation delivered within a trial. 
* `Frequency`: Frequency used for stimulation (Hz)
* `TotalStimDelivered`: Total duration in seconds of stimulation delivered within a trial (sum of all individual train durations).
* `PrevStimStop`: End of the last train of stimulation before the current trial starts (`EventStart`)   
* `NextStimStart`: Start of the first train of stimulation after the current trial ends (`EventStop`)
* `DiffPrevStim`: Difference in seconds between `EventStart` and `PrevStimStop`. Indicates how many seconds of NO stim were recorded before the trial started.
* `DiffNextStim`: Difference in seconds between `NextStimStart` and `EventStop`. Indicates how many seconds of NO stim were recorded after the trial ended.

### Columns associated with surveys identified for each trial:
[PENDING: Add description]
