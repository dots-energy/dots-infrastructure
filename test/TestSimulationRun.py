import base64
import unittest
import helics as h
import multiprocessing

from unittest.mock import MagicMock
from dots_infrastructure import HelperFunctions
from threading import Thread

from dots_infrastructure.DataClasses import HelicsCalculationInformation, PublicationDescription, SimulatorConfiguration, SubscriptionDescription
from dots_infrastructure.EsdlHelper import get_energy_system_from_base64_encoded_esdl_string
from dots_infrastructure.HelicsFederateHelpers import HelicsSimulationExecutor

BROKER_TEST_PORT = 23404

with open("C:\\Users\\20180029\\repos\\dots-infrastructure\\test\\test.esdl", mode="r") as esdl_file:
    encoded_base64_esdl = base64.b64encode(esdl_file.read().encode('utf-8')).decode('utf-8')

energy_system = get_energy_system_from_base64_encoded_esdl_string(encoded_base64_esdl)
HelicsSimulationExecutor.init_simulation = MagicMock(return_value=energy_system)

def create_pv_installation_simulator():
    HelperFunctions.get_simulator_configuration_from_environment = MagicMock(return_value=SimulatorConfiguration("PVInstallation", ["b8766109-5328-416f-9991-e81a5cada8a6", "176af591-6d9d-4751-bb0f-fac7e99b1c3d"], "Mock-PV", "127.0.0.1", BROKER_TEST_PORT, ["PVInstallation", "EConnection"]))

    publication_values = [
        PublicationDescription(True, "PVInstallation", "PV_Dispatch", "W", h.HelicsDataType.DOUBLE)
    ]

    subscriptions_values = []

    calculation_information = HelicsCalculationInformation(30, False, False, True, h.HelicsLogLevel.DEBUG, "PVInstallationDispatch", subscriptions_values, publication_values, MagicMock(return_value={
        "EConnectionDispatch", 0.75
    }))
    helics_simulation_executor = HelicsSimulationExecutor()
    helics_simulation_executor.add_calculation(calculation_information)
    helics_simulation_executor.start_simulation()

def create_e_connection_simulator():
    HelperFunctions.get_simulator_configuration_from_environment = MagicMock(return_value=SimulatorConfiguration("EConnection", ["f006d594-0743-4de5-a589-a6c2350898da"], "Mock-Econnection", "127.0.0.1", BROKER_TEST_PORT, ["PVInstallation", "EConnection"]))

    subscriptions_values = [
        SubscriptionDescription("PVInstallation", "PV_Dispatch", "W", h.HelicsDataType.DOUBLE)
    ]

    publication_values = [
        PublicationDescription(True, "EConnection", "EConnectionDispatch", "W", h.HelicsDataType.DOUBLE)
    ]

    calculation_information = HelicsCalculationInformation(60, False, False, True, h.HelicsLogLevel.DEBUG, "EConnectionDispatch", subscriptions_values, publication_values, MagicMock(return_value={
        "EConnectionDispatch", 0.25
    }))
    helics_simulation_executor = HelicsSimulationExecutor()
    helics_simulation_executor.add_calculation(calculation_information)
    helics_simulation_executor.start_simulation()


class TestSimulation(unittest.TestCase):

    MS_TO_BROKER_DISCONNECT = 60000

    def start_helics_broker(self):
        broker = h.helicsCreateBroker("zmq", "helics_broker_test", "-f 2 --loglevel=debug --timeout='60s'")
        broker.wait_for_disconnect(self.MS_TO_BROKER_DISCONNECT)

    
    def setUp(self):
        
        thread = Thread(target = self.start_helics_broker)
        thread.start()

    def test_simulation_run_starts_correctly(self):
        multiprocessing.set_start_method("spawn", force=False)
        e_connection_process = multiprocessing.Process(target = create_e_connection_simulator)
        e_connection_process._start_method
        e_connection_process.start()

        pv_panel_process = multiprocessing.Process(target = create_pv_installation_simulator)
        pv_panel_process.start()

        e_connection_process.join()
        pv_panel_process.join()

if __name__ == '__main__':
    unittest.main()