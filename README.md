# python-stage1-stimtab
Tool that allows tabulation of stage 1 stimulation efficacy data based on user-specified criteria.

Version: v1.0

Requirements: python>=3.8, pandas.

## User-specified variables/inputs:

* `OUTPUT_DIR`: string, path to directory in server where output CSV will be saved.
* `patient_id`: string, identifier of subject in presidio study (e.g. 'PR05', it won't accept 'pr05').
* `lead_on`: boolean, if set to True, trials/blocks will be identified by trains of stimulation delivered in the same lead, regardless of contact number. Mutually exclusive with variable `channels_on`.
* `channels_on`: boolean, if set to True, trials/blocks will be identified by trains of stimulations delivered in the same pair of contacts. For example, after 8 trains of stimulation in LVC2-3 the filter detectsthat the next train of stimulation is in LVC3-4. Then the filter will assign the last train in LVC2-3 as the end of the LVC2-3 trials, and the first train of LVC3-4 as the start of a new trial. Mutually exclusive with `lead_on`.
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
[TO DO: add description of each column in output file]  
