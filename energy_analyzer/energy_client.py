from enum import Enum
from typing import Dict, List, Union

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel

# Data point model with two properties - time and value
class DataPoint(BaseModel):
    timestamp: datetime
    value: float

# Define the type, Timeseries, as a list of Datapoints (which is a class)
Timeseries = List[DataPoint]

# Create enumerations for the measure type
class MeasureType(Enum):
    SCHEDULING = 1
    SAT_RESET = 2
    LED_RETROFIT = 3
    AHU_VFD = 4


# These values are hard-coded in this example, but represent an energy
# savings prediction that would normally vary over time.
# Your solution should account for situations where these values are not static.

# set the savings for each measure
_SAVINGS_BY_MEASURE = {
    MeasureType.SCHEDULING: 100,
    MeasureType.SAT_RESET: 200,
    MeasureType.LED_RETROFIT: 300,
    MeasureType.AHU_VFD: 400,
}

# takes a datetime 
def round_to_last_15m(dt: datetime) -> datetime:
    return dt - (dt - datetime.min) % timedelta(minutes=15)


class EnergyClient:
    # gets the expected energy useage in a Timeseries
    @staticmethod
    def get_building_expected_energy_usage(
        start: datetime, end: datetime
    ) -> Timeseries:
        """
        This API call will return a list of DataPoints that represents timeseries data at 15 minute intervals.

        The start and end dates determine the range of the result.

        Ex. result:
        [
            DataPoint(
                timestamp=2021-09-16 22:00:00,
                value=1000
            ),
            ...
            DataPoint(
                timestamp=2021-010-16 22:00:00,
                value=1000
            ),
        ]
        """
        current_time = round_to_last_15m(start)
        results = []

        while current_time < end:
            results.append(
                DataPoint(
                    timestamp=current_time,
                    # This value is hard-coded in this example,
                    # but represents an energy prediction that would normally vary over time.
                    value=1000,
                )
            )

            current_time += relativedelta(minutes=15)

        # Not used for the at-home challenge
        # time.sleep(3)

        return results

    # Get expected savings based on the measure type that is applied
    @staticmethod
    def get_measure_expected_energy_savings_for_generic_year(
         measure_type: MeasureType,
    ) -> Timeseries:
        """
        This API call will return a list of DataPoints that represents timeseries data at 15 minute intervals.

        The result represents the expected savings over an average year. The year will be set to `2010`, but
        that year should be ignored: this data represents an arbitrary year, not a specific year.

        Ex. result:
        [
            DataPoint(
                timestamp=2010-01-01 00:00:00,
                value=200
            ),
            ...
            DataPoint(
                timestamp=2010-12-21 23:45:00,
                value=200
            ),
        ]
        """
        current_time = datetime(year=2010, month=1, day=1)
        end = current_time + relativedelta(years=1)
        results = []

        while current_time < end:
            results.append(
                DataPoint(
                    timestamp=current_time, value=_SAVINGS_BY_MEASURE[measure_type]
                )
            )

            current_time += relativedelta(minutes=15)

        # Not used for the at-home challenge
        # time.sleep(3)

        return results

    def get_savings_for_time_period(start:datetime, end:datetime, startSavings:datetime, endSavings:datetime, measure_type:MeasureType):

        current_time = start
        results = []

        while current_time < end:
            if current_time > startSavings and current_time < endSavings:
                results.append(
                    DataPoint(
                        timestamp=current_time, value=_SAVINGS_BY_MEASURE[measure_type]
                    )
                )
            else: 
                results.append(
                    DataPoint(
                        timestamp=current_time, value=0
                    )
                )
            current_time += relativedelta(minutes=15)

        return results
