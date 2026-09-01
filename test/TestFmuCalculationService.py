from datetime import datetime
from pathlib import Path
from typing import List
import unittest
from dots_infrastructure.DataClasses import FmuInputVariable, FmuOutputVariable, SimulatorConfiguration, TimeStepInformation
from dots_infrastructure.GenericFMUCs import FmuCalculationService
from dots_infrastructure.test_infra.InfluxDBMock import InfluxDBMock
from esdl import EnergySystem
from esdl.esdl_handler import EnergySystemHandler
import helics as h

from dots_infrastructure import CalculationServiceHelperFunctions


BROKER_TEST_PORT = 23404
START_DATE_TIME = datetime(2024, 1, 1, 0, 0, 0)
SIMULATION_DURATION_IN_SECONDS = 1800
TEST_IDS = ["5c19dcff-b004-4644-99b9-f42d15a34f3a", "1412f71f-a9d2-4c66-a834-385cf91c3767"] 
INPUT_MAPPING_NAME = 'test-name'

def simulator_environment_e_connection():
    return SimulatorConfiguration("EConnection", TEST_IDS, "Mock-Econnection", "127.0.0.1", BROKER_TEST_PORT, "test-id", SIMULATION_DURATION_IN_SECONDS, START_DATE_TIME, "test-host", "test-port", "test-username", "test-password", "test-database-name", h.HelicsLogLevel.DEBUG, ["PVInstallation", "EConnection"])

class FmuModel(FmuCalculationService):

    def __init__(self):
        fmu_file_names = ["test_dots_2.fmu", "test_dots_3.fmu"] # specify this in child class
        fmu_paths : List[Path] = [Path(__file__).parent / "test_fmus" / file_name for file_name in fmu_file_names]
        inputs = [FmuInputVariable("variable_input", "bla", INPUT_MAPPING_NAME, "W")]
        outputs = [FmuOutputVariable("output_y", "bla", "W"), FmuOutputVariable("output_y2", "bla",  "W"), FmuOutputVariable("output_y3", "bla2",  "W")]
        super().__init__(fmu_paths, inputs, outputs)

class Test(unittest.TestCase):

    def read_esdl_file(self, file_path : str):
        esh = EnergySystemHandler()
        esh.load_file(file_path)
        return esh.get_energy_system()

    def setUp(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_connection
        test_esdl_path = Path(__file__).parent / "test_fmus" / "test-fmu.esdl"
        self.energy_system = self.read_esdl_file(str(test_esdl_path))
        self.test_input_name = f'bla/{INPUT_MAPPING_NAME}'

    def initialize_model(self, energy_system : EnergySystem):
        fmu_model = FmuModel()
        fmu_model.influx_connector = InfluxDBMock()
        fmu_model.init_calculation_service(energy_system)
        return fmu_model

    def test_when_service_is_initialized_calculation_is_correctly_initialized(self):
        fmu_model = FmuModel()
        fmu_model.init_calculation_service(self.energy_system)

        self.assertEqual(len(fmu_model.calculations), 1)
        added_calculation = fmu_model.calculations[0]
        self.assertEqual(len(added_calculation.helics_value_federate_info.inputs), 1)
        self.assertEqual(len(added_calculation.helics_value_federate_info.outputs), 2)
        self.assertEqual(added_calculation.helics_value_federate_info.outputs[0].data_type, h.HELICS_DATA_TYPE_VECTOR)
        self.assertEqual(added_calculation.helics_value_federate_info.outputs[1].data_type, h.HELICS_DATA_TYPE_DOUBLE)

    def test_when_service_is_initialized_parameters_are_set_on_fmu(self):
        test_cases = [
            {"esdl_id": TEST_IDS[0], "expected_output_y" : 60},
            {"esdl_id": TEST_IDS[1], "expected_output_y" : 100}
        ]
        for i in range(0, len(test_cases)):
            with self.subTest(i=i):
                test_case = test_cases[i]
                fmu_model = self.initialize_model(self.energy_system)

                param_dict = {}
                param_dict[self.test_input_name] = 1

                output_dict = fmu_model.fmu_calculation_step(param_dict, datetime(2024, 1, 1, 0, 15, 0), TimeStepInformation(1, 2), test_case['esdl_id'], self.energy_system)

                output_y_value = output_dict['output_y']
                self.assertEqual(test_case['expected_output_y'], output_y_value)

    def test_when_service_fmu_step_is_done_input_variable_is_set_correctly(self):
        test_cases = [
            {"esdl_id": TEST_IDS[0], "variable_input" : 2, "expected_output_y" : 120},
            {"esdl_id": TEST_IDS[0], "variable_input" : 3, "expected_output_y" : 180},
            {"esdl_id": TEST_IDS[1], "variable_input" : 2, "expected_output_y" : 200},
            {"esdl_id": TEST_IDS[1], "variable_input" : 3, "expected_output_y" : 300}
        ]
        for i in range(0, len(test_cases)):
            with self.subTest(i=i):
                test_case = test_cases[i]
                fmu_model = self.initialize_model(self.energy_system)

                param_dict = {}
                param_dict[self.test_input_name] = test_case['variable_input']

                output_dict = fmu_model.fmu_calculation_step(param_dict, datetime(2024, 1, 1, 0, 15, 0), TimeStepInformation(1, 2), test_case['esdl_id'], self.energy_system)

                output_y_value = output_dict['output_y']
                self.assertEqual(test_case['expected_output_y'], output_y_value)

    def test_when_entities_have_different_names_different_fmu_is_used(self):
        test_esdl_path = Path(__file__).parent / "test_fmus" / "test-fmu2.esdl"
        energy_system = self.read_esdl_file(str(test_esdl_path))
        test_cases = [
            {"esdl_id": TEST_IDS[0], "expected_output_y" : 60},
            {"esdl_id": TEST_IDS[1], "expected_output_y" : 50}
        ]
        for i in range(0, len(test_cases)):
            with self.subTest(i=i):
                test_case = test_cases[i]
                fmu_model = self.initialize_model(energy_system)

                param_dict = {}
                param_dict[self.test_input_name] = 1

                output_dict = fmu_model.fmu_calculation_step(param_dict, datetime(2024, 1, 1, 0, 15, 0), TimeStepInformation(1, 2), test_case['esdl_id'], energy_system)

                output_y_value = output_dict['output_y']
                self.assertEqual(test_case['expected_output_y'], output_y_value)


if __name__ == '__main__':
    unittest.main()
