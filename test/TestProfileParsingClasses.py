from dataclasses import dataclass
from datetime import datetime, timedelta

from esdl import DateTimeProfile, ProfileElement, StaticProfile, TimeSeriesProfile
import unittest

from dots_infrastructure.EsdlProfileParsingClasses import ParsedDateTimeProfile, ParsedTimeSeriesProfile, convert_parsed_datetime_profile_to_time_series_profile

@dataclass
class TestParamProfileClasses:
    profile : TimeSeriesProfile
    timestep : int
    expected_outcome : list[float]

class TestProfileClasses(unittest.TestCase):

    def setUp(self):
        super().setUp()
        date_time_profile = DateTimeProfile()
        date_time_profile.element.append(ProfileElement(from_=datetime(2020,1,1,22,0), to=datetime(2020,1,1,23,0), value=1.0))
        date_time_profile.element.append(ProfileElement(from_=datetime(2020,1,1,23,0), to=datetime(2020,1,2,0,0), value=2.0))
        date_time_profile.element.append(ProfileElement(from_=datetime(2020,1,2,0,0), to=datetime(2020,1,2,1,0), value=3.0))
        date_time_profile.element.append(ProfileElement(from_=datetime(2020,1,2,1,0), to=datetime(2020,1,2,2,0), value=4.0))
        date_time_profile.element.append(ProfileElement(from_=datetime(2020,1,2,2,0), to=datetime(2020,1,2,3,0), value=5.0))
        self.date_time_profile = date_time_profile
        self.time_series_profile = TimeSeriesProfile(startDateTime=datetime(2020,1,1,22,00), timestep=3600, values=[1.0,2.0,3.0,4.0,5.0])

    def parse_profile(self, example : StaticProfile):
        if isinstance(example, TimeSeriesProfile):
            return ParsedTimeSeriesProfile(example)
        if isinstance(example, DateTimeProfile):
            return ParsedDateTimeProfile(example)

    def test_given_parsed_profile_get_data_returns_correct_data(self):
        
        test_cases = [
            self.date_time_profile,
            self.time_series_profile
        ]
        for i, example in enumerate(test_cases):
            with self.subTest(i=i, params = example):
                parsed_profile = self.parse_profile(example)

                from_date = datetime(2020,1,1,23,0)
                to_date = datetime(2020,1,2,2,0)
                data = parsed_profile.get_data(from_date, to_date)
                self.assertListEqual(data, [2,3,4])

    def test_getting_time_series_value_is_implemented_correctly(self):
        test_cases = [
            TestParamProfileClasses(self.time_series_profile, 3600, [2.0, 3.0, 4.0]),
            TestParamProfileClasses(self.time_series_profile, 900, [2.0, 2.0, 2.0 ,2.0, 3.0, 3.0, 3.0, 3.0, 4.0, 4.0, 4.0, 4.0]),
        ]
        for i, example in enumerate(test_cases):
            with self.subTest(i=i, params = example):
                parsed_profile = self.parse_profile(example.profile)

                from_date = datetime(2020,1,1,23,0)
                to_date = datetime(2020,1,2,2,0)
                data = parsed_profile.get_data_in_timeseries_format(from_date, to_date, example.timestep)
                self.assertListEqual(data, example.expected_outcome)

    def test_converting_datetime_profile_to_timeseries(self):
        test_cases = [
            self.date_time_profile,
        ]
        for i, profile in enumerate(test_cases):
            with self.subTest(i=i, params = profile):
                parsed_profile = self.parse_profile(profile)
                time_series_profile = convert_parsed_datetime_profile_to_time_series_profile(parsed_profile)

                new_all_data = time_series_profile.get_data(time_series_profile.min_date, time_series_profile.max_date)
                self.assertEqual(new_all_data, [1.0,2.0,3.0,4.0,5.0])


    

if __name__ == '__main__':
    unittest.main()