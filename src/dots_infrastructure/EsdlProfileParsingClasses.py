from datetime import datetime, timedelta
import math

from dots_infrastructure.DataClasses import EsdlId
from esdl import DateTimeProfile, StaticProfile, TimeSeriesProfile
import pandas as pd

class ParsedStaticProfile:

    def __init__(self, data : StaticProfile):
        self._parsed_profile = self._parse_profile(data)
        self.min_date : datetime = datetime.min
        self.max_date : datetime = datetime.max
    
    def _parse_profile(self, profile):
        # Needs to be implemented by child classes
        pass

    def get_data(self, from_data : datetime, to_data : datetime):
        """
        Get all the data within a timewindow the outputted data will include al values >= from_data and <= to_data

        Args:
            from_data: The timestamp where the timeseries should start.
            to_data: The timestamp where the timeseries should stop.

        Returns:
            The values in the time window
        """
        pass

    def _alter_year_to_match_data(self, from_data : datetime, to_data : datetime) -> tuple[datetime, datetime]:
        if self.min_date <= from_data <= self.max_date and self.min_date <= to_data <= self.max_date:
            return from_data, to_data

        delta_t_data : timedelta = to_data - from_data

        from_data_in_data = datetime(self.min_date.year, from_data.month, from_data.day, from_data.hour, from_data.minute, from_data.second, tzinfo=from_data.tzinfo)
        to_date_in_data = from_data_in_data + delta_t_data

        # Try to find first ranged contained within the data
        year = self.min_date.year
        while not (self.min_date <= from_data_in_data <= self.max_date and self.min_date <= to_date_in_data <= self.max_date):
            year += 1
            from_data_in_data = datetime(year, from_data.month, from_data.day, from_data.hour, from_data.minute, from_data.second, tzinfo=from_data.tzinfo)
            to_date_in_data = from_data_in_data + delta_t_data

        return from_data_in_data, to_date_in_data

class ParsedDateTimeProfile(ParsedStaticProfile):

    def __init__(self, data):
        super().__init__(data)
        parsed_profile : pd.DataFrame = self._parsed_profile
        self.min_date = parsed_profile["from"].min()
        self.max_date = parsed_profile["to"].max()
        self._is_time_series = False

    def _parse_profile(self, profile : DateTimeProfile) -> pd.DataFrame:
        # Parse the profile and return the values
        from_profile = []
        to_profile = []
        value_profile = []
        prev_time_delta = -1
        time_delta_consistent = True
        for el in profile.element:
            value_profile.append(el.value)
            from_profile.append(el.from_)
            to_profile.append(el.to)
            time_delta = el.to - el.from_
            if prev_time_delta == -1:
                prev_time_delta = time_delta
            if prev_time_delta != time_delta:
                time_delta_consistent = False

        self._is_time_series = time_delta_consistent

        ret_val = pd.DataFrame({
            "from": from_profile,
            "to": to_profile,
            "value": value_profile
        })
        ret_val.sort_values("from")
        return ret_val


    def get_data(self, from_data : datetime, to_data : datetime):
        from_data_altered_year, to_data_altered_year = self._alter_year_to_match_data(from_data, to_data)
        data : pd.DataFrame = self._parsed_profile
        data_filtered = data[(data["from"] >= from_data_altered_year ) & (data["to"] <= to_data_altered_year )]
        values = data_filtered["value"].tolist()
        return values
    


class ParsedTimeSeriesProfile(ParsedStaticProfile):

    def __init__(self, data):
        super().__init__(data)
        parsed_profile : TimeSeriesProfile = self._parsed_profile
        self.min_date : datetime = parsed_profile.startDateTime
        self.max_date : datetime = parsed_profile.startDateTime + timedelta(seconds=len(parsed_profile.values) * parsed_profile.timestep)

    def _parse_profile(self, profile : TimeSeriesProfile):
        return profile
    
    def get_data_in_timeseries_format(self, from_data : datetime, to_data : datetime, time_step_seconds : float):
        """
        Get the data as consistent timeseries coherent to a specific timestep size.
        The 'time_step_seconds' parameter should be smaller than or equal to and a multiple of the underlying profile's timestep

        Args:
            from_data: The timestamp where the timeseries should start.
            to_data: The timestamp where the timeseries should stop.
            time_step_seconds: The timestep of the outputted timeseries.

        Returns:
            A time series with a time delta of 'time_step_seconds'.
        """
        data : TimeSeriesProfile = self._parsed_profile
        if not (time_step_seconds <= data.timestep and data.timestep % time_step_seconds == 0):
            raise ValueError("time_step_in_seconds must be a multiple of the underlying timestep and <= the underlying timestep")
        ret_val = []
        from_data_altered_year, to_data_altered_year = self._alter_year_to_match_data(from_data, to_data)
        time_step_horizion_date = from_data_altered_year
        while time_step_horizion_date + timedelta(seconds=time_step_seconds) <= to_data_altered_year:
            new_value = self.get_data(time_step_horizion_date, time_step_horizion_date + timedelta(seconds=time_step_seconds))
            ret_val.extend(new_value)
            time_step_horizion_date = time_step_horizion_date + timedelta(seconds=time_step_seconds)

        return ret_val

    def get_data(self, from_data : datetime, to_data : datetime):
        data : TimeSeriesProfile = self._parsed_profile

        from_data_in_data, to_data_in_data = self._alter_year_to_match_data(from_data, to_data)

        delta_t_from : timedelta = from_data_in_data - data.startDateTime
        delta_t_to : timedelta = to_data_in_data - data.startDateTime

        from_index = math.floor(delta_t_from.seconds / data.timestep)
        to_index = math.ceil(delta_t_to.seconds / data.timestep)
        values = data.values[from_index:to_index]
        return values