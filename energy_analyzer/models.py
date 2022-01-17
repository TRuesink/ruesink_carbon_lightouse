from collections import defaultdict
from datetime import datetime
from typing import List, Optional

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel

from energy_client import EnergyClient, MeasureType, Timeseries, DataPoint


# takes the current date time, and get the first day of the current month (keep year the same)
# Example if its 1/15/2022, the function returns 1/1/2022
def get_first_moment_of_month(now: datetime) -> datetime:
    return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


class Fault(BaseModel):  # Not used for the at-home challenge
    """
    This model represents a Faulty measure, and is used to adjust the savings
    of a measure over a specific time range. For a given measure, you can
    assume that there are no overlapping faults.
    """

    name: str
    fault_factor: float = 1
    start: datetime
    end: datetime


class Measure(BaseModel):
    """
    This model represents an Energy Efficiency Measure, including a time range that
    describes when that measure was implemented / active on a building.
    """

    name: str
    measure_type: MeasureType
    faults: Optional[List[Fault]]  # not used for the at-home challenge
    start: datetime
    end: datetime

    # Implement this function for the at home challenge
    def get_savings_for_date_range(self, start: datetime, end: datetime) -> Timeseries:
        """
        Takes in a start and end date and returns the expected measure savings. For example,
        when this function is called from `get_past_and_future_year_of_monthly_energy_usage`,
        it should return timeseries data that matches the shape of the building energy usage
        data.

        A correct solution will account for whether the measure is active or not during the
        given time range.
        """
        # SOLUTION 1: CREATE A SAVINGS MODEL BASED ON A GENERIC YEAR OF SAVINGS FOR SPECIFIC MEASURE
        # Get the generic year model for Expected energy savings
        generic_year_savings = EnergyClient.get_measure_expected_energy_savings_for_generic_year(self.measure_type)
        # create a dictionary with timestamp of each datapoint as the key
        generic_year_savings_dict = {datapoint.timestamp: datapoint.value for datapoint in generic_year_savings}

        current_time = start
        results = []

        # add datapoints to result array between start and end times
        while current_time < end:
            if self.start < current_time < self.end:
                # if the current time is within the range of the measures start and end times
                # replace the current time year with that of the model year (2010)
                current_time_in_model_year = current_time.replace(year=2010)
                # add an energy savings datapoint to the results array
                results.append(DataPoint(timestamp=current_time, value=generic_year_savings_dict[current_time_in_model_year]))
            else:
                # if the current time is not within the range, add a datapoint with 0 savings
                results.append(DataPoint(timestamp=current_time, value=0))
            # increment the time 
            current_time += relativedelta(minutes=15)

        
        return results
        # SOLUTION 2: CREATE ENERGY SAVINGS MODEL USING A METHOD FROM ENERGY CLIENT
        # return EnergyClient.get_savings_for_time_period(start, end, self.start, self.end,self.measure_type)



class Building(BaseModel):
    """
    This model represents the overall Building in which we are looking to reduce energy usage.
    Each Building has a list of Energy Efficiency Measures which provide energy savings over
    a given time frame.
    """

    name: str
    measures: Optional[List[Measure]]

    def get_past_and_future_year_of_monthly_energy_usage(
        self, include_measure_savings: Optional[bool] = False
    ) -> Timeseries:
        # set now to a datetime for the first day of the current month and year
        now = get_first_moment_of_month(datetime.now())
        # set the start time to 1 year prior
        start = now - relativedelta(years=1)
        # set the end time to 1 year in the future
        end = now + relativedelta(years=1)

        quarter_hourly_usage_data = EnergyClient.get_building_expected_energy_usage(
            start, end
        )

        if include_measure_savings:
            # this code will break until you implement `measure.get_savings_for_date_range`
            # for each measure in this buildings list of measures, get thes avings for the date range
            savings_by_measure = [
                measure.get_savings_for_date_range(start, end)
                for measure in self.measures
            ]

            for usage_data, *savings_data_args in zip(
                quarter_hourly_usage_data, *savings_by_measure
            ):
                for savings_data in savings_data_args:
                    usage_data.value -= savings_data.value

        # Init list to store monthly usage. if a value for key has not yet been defined, its 0.
        monthly_usage = defaultdict(int)
        for quarter_hour_usage in quarter_hourly_usage_data:
            # for each datapoint get the month of the datetime of that datapoint.
            month_timestamp = get_first_moment_of_month(quarter_hour_usage.timestamp)
            # add the quarter hour usage to the current month
            monthly_usage[month_timestamp] += quarter_hour_usage.value

        # return a list of datapoints
        return [DataPoint(timestamp=ts, value=v) for ts, v in monthly_usage.items()]
