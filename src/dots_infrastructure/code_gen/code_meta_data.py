from dataclasses import dataclass
from typing import List

from dataclasses_json import DataClassJsonMixin

@dataclass
class CalculationServiceInputData(DataClassJsonMixin):
    name : str
    esdl_type : str
    description : str
    unit : str
    data_type : str


@dataclass
class CalculationServiceOutputData(DataClassJsonMixin):
    name : str
    description : str
    unit : str
    data_type : str


@dataclass
class Calculation(DataClassJsonMixin):
    name : str
    description : str
    time_period_in_seconds : int
    offset_in_seconds : int
    inputs : List[CalculationServiceInputData]
    outputs : List[CalculationServiceOutputData]
    calculation_function_name : str | None = None


@dataclass
class CalculationServiceMetaData(DataClassJsonMixin):
    name : str
    esdl_type : str
    description : str
    calculations : List[Calculation]