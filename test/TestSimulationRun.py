import base64
from datetime import datetime
import random
import unittest
import helics as h
import multiprocessing

from unittest.mock import MagicMock
from dots_infrastructure import HelperFunctions

from dots_infrastructure.DataClasses import EsdlId, HelicsCalculationInformation, PublicationDescription, SimulatorConfiguration, SubscriptionDescription
from dots_infrastructure.EsdlHelper import get_energy_system_from_base64_encoded_esdl_string
from dots_infrastructure.HelicsFederateHelpers import HelicsSimulationExecutor
from dots_infrastructure.Logger import LOGGER
from infra.InfluxDBMock import InfluxDBMock

BROKER_TEST_PORT = 23404
START_DATE_TIME = datetime(2024, 1, 1, 0, 0, 0)
SIMULATION_DURATION_IN_SECONDS = 960

with open("C:\\Users\\20180029\\repos\\dots-infrastructure\\test\\test.esdl", mode="r") as esdl_file:
    encoded_base64_esdl = base64.b64encode(esdl_file.read().encode('utf-8')).decode('utf-8')

HelicsSimulationExecutor._get_esdl_from_so = MagicMock(return_value=get_energy_system_from_base64_encoded_esdl_string(encoded_base64_esdl))

MS_TO_BROKER_DISCONNECT = 60000

def start_helics_broker():
    broker = h.helicsCreateBroker("zmq", "helics_broker_test", "-f 3 --loglevel=debug --timeout='60s'")
    broker.wait_for_disconnect(MS_TO_BROKER_DISCONNECT)

def simulator_environment_e_pv():
    return SimulatorConfiguration("PVInstallation", ['176af591-6d9d-4751-bb0f-fac7e99b1c3d','b8766109-5328-416f-9991-e81a5cada8a6'], "Mock-PV", "127.0.0.1", BROKER_TEST_PORT, "test-id", SIMULATION_DURATION_IN_SECONDS, START_DATE_TIME, "test-host", "test-port", "test-username", "test-password", "test-database-name", ["PVInstallation", "EConnection"])

class CalculationServicePVDispatch(HelicsSimulationExecutor):

    def __init__(self, output_file_name):
        HelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_pv
        super().__init__()
        self.influx_connector = InfluxDBMock(output_file_name)
        publictations_values = [
            PublicationDescription(True, "PVInstallation", "PV_Dispatch", "W", h.HelicsDataType.DOUBLE)
        ]
        subscriptions_values = []

        pv_installation_period_in_seconds = 30
        info = HelicsCalculationInformation(pv_installation_period_in_seconds, False, False, True, h.HelicsLogLevel.DEBUG, "pvdispatch_calculation", subscriptions_values, publictations_values, self.pvdispatch_calculation)
        self.add_calculation(info)


    def pvdispatch_calculation(self, param_dict : dict, simulation_time : datetime, esdl_id : EsdlId):
        ret_val = {}
        LOGGER.info(f"Executing pvdispatch_calculation")
        ret_val["PV_Dispatch"] = 0.25 * random.randint(1,20)
        self.influx_connector.set_time_step_data_point(esdl_id, "PV_Dispatch", simulation_time, ret_val["PV_Dispatch"])
        return ret_val

def simulator_environment_e_connection():
    return SimulatorConfiguration("EConnection", ["f006d594-0743-4de5-a589-a6c2350898da"], "Mock-Econnection", "127.0.0.1", BROKER_TEST_PORT, "test-id", SIMULATION_DURATION_IN_SECONDS, START_DATE_TIME, "test-host", "test-port", "test-username", "test-password", "test-database-name", ["PVInstallation", "EConnection"])

class CalculationServiceEConnection(HelicsSimulationExecutor):

    def __init__(self, output_file_name):
        HelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_connection
        super().__init__()
        self.influx_connector = InfluxDBMock(output_file_name)

        subscriptions_values = [
            SubscriptionDescription("PVInstallation", "PV_Dispatch", "W", h.HelicsDataType.DOUBLE)
        ]

        publication_values = [
            PublicationDescription(True, "EConnection", "EConnectionDispatch", "W", h.HelicsDataType.DOUBLE)
        ]

        e_connection_period_in_seconds = 60

        calculation_information = HelicsCalculationInformation(e_connection_period_in_seconds, False, False, True, h.HelicsLogLevel.DEBUG, "EConnectionDispatch", subscriptions_values, publication_values, self.e_connection_dispatch)
        self.add_calculation(calculation_information)

        publication_values = [
            PublicationDescription(True, "EConnection", "Schedule", "W", h.HelicsDataType.VECTOR)
        ]

        e_connection_period_scedule_in_seconds = 120

        calculation_information_schedule = HelicsCalculationInformation(e_connection_period_scedule_in_seconds, False, False, True, h.HelicsLogLevel.DEBUG, "EConnectionSchedule", [], publication_values, self.e_connection_da_schedule)
        self.add_calculation(calculation_information_schedule)

    def e_connection_dispatch(self, param_dict : dict, simulation_time : datetime, esdl_id : EsdlId):
        pv_dispatch = HelperFunctions.get_single_param_with_name(param_dict, "PV_Dispatch")
        ret_val = {}
        LOGGER.info(f"Executing e_connection_dispatch with pv dispatch value {pv_dispatch}")
        ret_val["EConnectionDispatch"] = pv_dispatch * random.randint(1,3)
        self.influx_connector.set_time_step_data_point(esdl_id, "EConnectionDispatch", simulation_time, ret_val["EConnectionDispatch"])
        return ret_val
    
    def e_connection_da_schedule(self, param_dict : dict, simulation_time : datetime, esdl_id : EsdlId):
        ret_val = {}
        ret_val["Schedule"] = [1.0,2.0,3.0]
        LOGGER.info(f"Executing e_connection_da_schedule")
        self.influx_connector.set_time_step_data_point(esdl_id, "DAScedule", simulation_time, ret_val["Schedule"])
        return ret_val

class TestSimulation(unittest.TestCase):

    def test_simulation_run_starts_correctly(self):
        # Arrange 
        broker_process = multiprocessing.Process(target = start_helics_broker)
        broker_process.start()

        e_connection_output_file = "e_connection_out.txt"
        pv_installation_output_file = "pv_installation_out.txt"
        e_connection_dispatch_period_in_seconds = 60
        e_connection_period_scedule_in_seconds = 120
        pv_period = 30

        # Execute
        cs_econnection = CalculationServiceEConnection(e_connection_output_file)
        cs_dispatch = CalculationServicePVDispatch(pv_installation_output_file)

        cs_econnection.start_simulation()
        cs_dispatch.start_simulation()
        cs_econnection.stop_simulation()
        cs_dispatch.stop_simulation()

        # Assert
        with open(e_connection_output_file, 'r') as f:
            lines = f.readlines()
        self.assertEqual(len(lines), SIMULATION_DURATION_IN_SECONDS / e_connection_dispatch_period_in_seconds + SIMULATION_DURATION_IN_SECONDS / e_connection_period_scedule_in_seconds)

        with open(pv_installation_output_file, 'r') as f:
            lines = f.readlines()
        self.assertEqual(len(lines), SIMULATION_DURATION_IN_SECONDS / pv_period * 2)


if __name__ == '__main__':
    unittest.main()