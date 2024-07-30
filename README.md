# python-stage1-stimtab
Tool that allows tabulation of stage 1 stimulation efficacy data based on user-specified criteria

Requirements: python>=3.8

## User-specified variables/inputs:

* 'OUTPUT_DIR': str, path to directory in server where output CSV will be saved.
* 'patient_id': str, identifier of subject in presidio study.
* 'lead_on': bool, if set to True, trials/blocks will be identified by trains of stimulation delivered in the same lead, regardless of contact number. Mutually exclusive with variable 'channels_on'.
* 'channels_on': bool, if set to True, trials/blocks will be identified by trains of stimulations delivered in the same pair of contacts. For example, after 8 trains of stimulation in LVC2-3 the filter detectsthat the next train of stimulation is in LVC3-4. Then the filter will assign the last train in LVC2-3 as the end of the LVC2-3 trials, and the first train of LVC3-4 as the start of a new trial. Mutually exclusive with 'lead_on'.
* 'frequency_on': bool, if set to True, frequency of stimulation will be considered as a criteria for trials/blocks identification. Optional and can be used in addition to other variables. 
* 'amplitude_on': bool, if set to True, amplitude of stimulation will be considered as criteria for trials/blocks identification. Optional and can be used in addition to other variables. 
* 'time_threshold': float, indicates maximum time in seconds between the end and start of trains of stimulation that have same filter parameters. 
* 'total_stim_duration': float, indicates minimum total time in seconds of stimulation delivered within a trial/block. This is applied AFTER trials/blocks have been identified and labeled. Optional and can be used if you only want to output trials/blocks in which we delivered X seconds or more of total stimulation, otherwise set to 0.
* 'pre_stim_duration': float, indicates minimum time in seconds of NO stimulation before delivering the first train in a trial/block. This is applied AFTER trials/blocks have been identified and labeled. Optional and can be used if you only want to output trials/blocks that have X seconds or more of no stimulation before the trial started. 
* 'post_stim_duration': float, indicates minimum time in seconds of NO stimulation after delivering the last train in a trial/block. This is applied AFTER trials/blocks have been identified and labeled. Optional and can be used if you only want to output trials/blocks that have X seconds or more of no stimulation after the trial ended.

     
## tools.py
Custom functions called in "filter.py":
### LoadRawData
function that loads CSV file found in Google Drive according to "patient id" variable. 
