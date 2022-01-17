# Carbon Lighthouse Coding Challenge - Tim Ruesink

Instructions:
* Clone this repo
* navigate to parent directory
```bash
cd ruesink_carbon_lighthouse
```
* run the `install.sh` script.
```bash
sh install.sh
```
* activate the venv 
```bash
source ./bin/activate
```
* run tests
```bash
python energy_analyzer/test_biz_logic.py
```


### SOLUTION 1 for `get_savings_for_date_range`
Solution 1 uses the EnergyClient method, `get_measure_expected_energy_savings_for_generic_year` to fetch a generic year Timeseries of energy savigns datapoints. It From that timeseries, it creates a dict with the timestamp as the key and the savings value as the dict value. A results array is initialized and datapoints are added in 15 minute increments for the start timestamp to the end timestamp. If the current datapoint timestamp is between the measure start time and end time, create a variable for the current time with the year being the year of the generic savings model. If this is the case add a datapoint with a timestamp equal to the current time and a value equal to the generic savings model value at the current time in the model year (2010 in this case).

This solution assumes I was not able to alter / add methods to the energy client api.

### SOLUTION 2 for `get_savings_for_date_range`
Solution 2 utilizes a new API method `get_savings_for_time_period`. This method takes a start time, end time, start of savings time, end of savings time, and a measure type. First, I set the current time to the start time. I append a datapoint to an array in 15 minute increments (updating the current time in each loop). if the current time is in range of the start of savings and end of savings, append a datapoint with a value equal to that measures value. If not, append a datapoint with a value of 0. 



