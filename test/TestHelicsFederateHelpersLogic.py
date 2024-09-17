from datetime import datetime
import unittest
from unittest.mock import MagicMock, patch

from esdl import EnergySystem
import helics as h

from dots_infrastructure import CalculationServiceHelperFunctions, Common
from dots_infrastructure.Constants import TimeRequestType
from dots_infrastructure.DataClasses import EsdlId, HelicsCalculationInformation, PublicationDescription, SimulatorConfiguration, SubscriptionDescription, TimeStepInformation
from dots_infrastructure.HelicsFederateHelpers import HelicsCombinationFederateExecutor, HelicsSimulationExecutor
from dots_infrastructure.Logger import LOGGER

LOGGER.disabled = True

def simulator_environment_e_connection():
    return SimulatorConfiguration("EConnection", ["f006d594-0743-4de5-a589-a6c2350898da"], "Mock-Econnection", "127.0.0.1", 2000, "test-id", 900, datetime(2024,1,1), "test-host", "test-port", "test-username", "test-password", "test-database-name", h.HelicsLogLevel.DEBUG, ["PVInstallation", "EConnection"])

def simulator_environment_e_logic_test():
    return SimulatorConfiguration("LogicTest", ["f006d594-0743-4de5-a589-a6c2350898da"], "Mock-LogicTest", "127.0.0.1", 2000, "test-id", 5, datetime(2024,1,1), "test-host", "test-port", "test-username", "test-password", "test-database-name", h.HelicsLogLevel.DEBUG, ["PVInstallation", "EConnection"])

class CalculationServiceEConnection(HelicsSimulationExecutor):

    def __init__(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_connection
        super().__init__()

        subscriptions_values = [
            SubscriptionDescription("PVInstallation", "PV_Dispatch", "W", h.HelicsDataType.DOUBLE)
        ]

        e_connection_period_in_seconds = 60

        calculation_information = HelicsCalculationInformation(time_period_in_seconds=e_connection_period_in_seconds, 
                                                               time_request_type=TimeRequestType.PERIOD,
                                                               offset=0,
                                                               wait_for_current_time_update=False, 
                                                               uninterruptible=False, 
                                                               terminate_on_error=True, 
                                                               calculation_name="EConnectionDispatch", 
                                                               inputs=subscriptions_values, 
                                                               outputs=None, 
                                                               calculation_function=self.e_connection_dispatch)
        self.add_calculation(calculation_information)

        publication_values = [
            PublicationDescription(True, "EConnection", "Schedule", "W", h.HelicsDataType.VECTOR)
        ]

        e_connection_period_scedule_in_seconds = 120

        calculation_information_schedule = HelicsCalculationInformation(time_period_in_seconds=e_connection_period_scedule_in_seconds,
                                                                        time_request_type=TimeRequestType.PERIOD,
                                                                        offset=0, 
                                                                        wait_for_current_time_update=False, 
                                                                        uninterruptible=False, 
                                                                        terminate_on_error=True, 
                                                                        calculation_name="EConnectionSchedule", 
                                                                        inputs=None, 
                                                                        outputs=publication_values, 
                                                                        calculation_function=self.e_connection_da_schedule)
        self.add_calculation(calculation_information_schedule)

    def e_connection_dispatch(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):

        return 0
    
    def e_connection_da_schedule(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        return [1.0,2.0,3.0]

class TestLogicAddingCalculations(unittest.TestCase):
    def test_simulation_none_input_output_sets_empty_inputs_and_outputs(self):

        # Execute
        cs_econnection = CalculationServiceEConnection()

        # Assert
        self.assertEqual(len(cs_econnection.calculations), 2)
        self.assertEqual(len(cs_econnection.calculations[0].helics_value_federate_info.inputs), 1)
        self.assertEqual(len(cs_econnection.calculations[0].helics_value_federate_info.outputs), 0)
        self.assertEqual(len(cs_econnection.calculations[1].helics_value_federate_info.inputs), 0)
        self.assertEqual(len(cs_econnection.calculations[1].helics_value_federate_info.outputs), 1)

class TestLogicRunningSimulation(unittest.TestCase):

    def setUp(self):
        self.federate_get_name = h.helicsFederateGetName
        self.common_terminate_requested = Common.terminate_requested_at_commands_endpoint
        self.get_sim_config_from_env = CalculationServiceHelperFunctions.get_simulator_configuration_from_environment 
        self.fed_eneter_executing_mode = h.helicsFederateEnterExecutingMode
        self.get_time_property = h.helicsFederateGetTimeProperty 
        self.request_time = h.helicsFederateRequestTime 
        h.helicsFederateGetName = MagicMock(return_value = "LogicTest")
        Common.terminate_requested_at_commands_endpoint = MagicMock()
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_logic_test
        h.helicsFederateEnterExecutingMode = MagicMock()
        h.helicsFederateGetTimeProperty = MagicMock(return_value = 5)
        h.helicsFederateRequestTime = MagicMock(return_value = 5)

    def tearDown(self) -> None:
        h.helicsFederateGetName = self.federate_get_name
        Common.terminate_requested_at_commands_endpoint = self.common_terminate_requested
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = self.get_sim_config_from_env 
        h.helicsFederateEnterExecutingMode = self.fed_eneter_executing_mode
        h.helicsFederateGetTimeProperty = self.get_time_property
        h.helicsFederateRequestTime = self.request_time

    def test_helics_simulation_loop_started_correctly(self):
        calculation_information_schedule = HelicsCalculationInformation(time_period_in_seconds=5,
                                                                        time_request_type=TimeRequestType.PERIOD,
                                                                        offset=0,
                                                                        wait_for_current_time_update=False, 
                                                                        uninterruptible=False, 
                                                                        terminate_on_error=True, 
                                                                        calculation_name="EConnectionSchedule", 
                                                                        inputs=[], 
                                                                        outputs=[], 
                                                                        calculation_function=MagicMock(return_value=5))
        self.federate_executor = HelicsCombinationFederateExecutor(calculation_information_schedule)

        # Execute
        self.federate_executor.enter_simulation_loop()

        # Assert
        h.helicsFederateEnterExecutingMode.assert_called_once()
        calculation_information_schedule.calculation_function.assert_called_once_with({}, datetime(2024, 1, 1, 0, 0, 5), TimeStepInformation(1,1), 'f006d594-0743-4de5-a589-a6c2350898da', None)

    def test_when_time_request_type_period_helicsFederateRequestTime_called_with_period(self):
        # arrange
        calculation_information_schedule = HelicsCalculationInformation(time_period_in_seconds=5,
                                                                        time_request_type=TimeRequestType.PERIOD,
                                                                        offset=0,
                                                                        wait_for_current_time_update=False, 
                                                                        uninterruptible=False, 
                                                                        terminate_on_error=True, 
                                                                        calculation_name="EConnectionSchedule", 
                                                                        inputs=[], 
                                                                        outputs=[], 
                                                                        calculation_function=MagicMock(return_value=5))
        self.federate_executor = HelicsCombinationFederateExecutor(calculation_information_schedule)

        # Execute
        self.federate_executor.enter_simulation_loop()

        # Assert
        h.helicsFederateRequestTime.assert_called_once_with(None, 0)

    def test_when_time_request_type_on_input_helicsFederateRequestTime_called_with_helics_max_time(self):
        # arrange
        calculation_information_schedule = HelicsCalculationInformation(time_period_in_seconds=5,
                                                                        time_request_type=TimeRequestType.ON_INPUT,
                                                                        offset=0,
                                                                        wait_for_current_time_update=False, 
                                                                        uninterruptible=False, 
                                                                        terminate_on_error=True, 
                                                                        calculation_name="EConnectionSchedule", 
                                                                        inputs=[], 
                                                                        outputs=[], 
                                                                        calculation_function=MagicMock(return_value=5))
        self.federate_executor = HelicsCombinationFederateExecutor(calculation_information_schedule)

        # Execute
        self.federate_executor.enter_simulation_loop()

        # Assert
        h.helicsFederateRequestTime.assert_called_once_with(None, h.HELICS_TIME_MAXTIME)

if __name__ == '__main__':
    unittest.main()