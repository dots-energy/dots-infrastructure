# -*- coding: utf-8 -*-
import random
import matplotlib.pyplot as plt
import helics as h
import logging
import numpy as np

from dots_infrastructure.DotsInfrastructure import HelicsCalculationInformation, HelicsSimulationExecutor, PublicationDescription,  SubscriptionDescription, generate_publications_from_value_descriptions, generate_subscriptions_from_value_descriptions, get_simulator_configuration_from_environment, get_single_param_with_name


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

def charger_calculation(param_dict : dict):
    ev_current = get_single_param_with_name(param_dict, "EV_current")
    logger.info(f"Executing charger calculation with ev_current: {ev_current}")
    ret_val = {}
    ret_val["EV_voltage"] = ev_current * random.randint(1,3)
    return ret_val


if __name__ == "__main__":

    simulator_configuration = get_simulator_configuration_from_environment()

    subscriptions_values = [
        SubscriptionDescription("PVInstallation", "EV_current", "A", h.HelicsDataType.DOUBLE)
    ]
    publictations_values = [
        PublicationDescription(True, "EConnection", "EV_voltage", "V", h.HelicsDataType.DOUBLE)
    ]

    simulator_configuration = get_simulator_configuration_from_environment()

    subscriptions_values = generate_subscriptions_from_value_descriptions(subscriptions_values, simulator_configuration)
    publication_values = generate_publications_from_value_descriptions(publictations_values, simulator_configuration)
    calculation_information = HelicsCalculationInformation(30, False, False, True, h.HelicsLogLevel.DEBUG, "battery_calculation", subscriptions_values, publication_values, charger_calculation)
    helics_simulation_executor = HelicsSimulationExecutor()
    helics_simulation_executor.add_calculation(calculation_information)
    helics_simulation_executor.start_simulation()