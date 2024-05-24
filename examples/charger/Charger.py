# -*- coding: utf-8 -*-
"""
Created on 9/28/2020

This is a simple battery value federate that models the physics of an EV
battery as it is being charged. The federate receives a voltage signal
representing the voltage applied to the charging terminals of the battery
and based on its internally modeled SOC, calculates the current draw of
the battery and sends it back to the EV federate. Note that this SOC should
be considered the true SOC of the battery which may be different than the
SOC modeled by the charger. Each battery ceases charging when its SOC reaches 100%.

@author: Trevor Hardy
trevor.hardy@pnnl.gov
"""

import random
import matplotlib.pyplot as plt
import helics as h
import logging
import numpy as np

from dots_infrastructure import SubscriptionDescription, PublicationDescription, HelicsFederateExecutor, HelicValueFederateInformation, generate_publications_from_value_descriptions, generate_subscriptions_from_value_descriptions, get_simulator_configuration_from_environment, get_single_param_with_name


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


def destroy_federate(fed):
    """
    As part of ending a HELICS co-simulation it is good housekeeping to
    formally destroy a federate. Doing so informs the rest of the
    federation that it is no longer a part of the co-simulation and they
    should proceed without it (if applicable). Generally this is done
    when the co-simulation is complete and all federates end execution
    at more or less the same wall-clock time.

    :param fed: Federate to be destroyed
    :return: (none)
    """
    
    # Adding extra time request to clear out any pending messages to avoid
    #   annoying errors in the broker log. Any message are tacitly disregarded.
    grantedtime = h.helicsFederateRequestTime(fed, h.HELICS_TIME_MAXTIME)
    status = h.helicsFederateDisconnect(fed)
    h.helicsFederateDestroy(fed)
    logger.info("Federate finalized")


def get_new_battery(numBattery):
    """
    Using hard-coded probabilities, a distribution of batteries of
    fixed battery sizes are generated. The number of batteries is a user
    provided parameter.

    :param numBattery: Number of batteries to generate
    :return
        listOfBatts: List of generated batteries

    """

    # Probabilities of a new EV battery having small capacity (sm),
    # medium capacity (med), and large capacity (lg).
    sm = 0.2
    med = 0.2
    lg = 0.6

    # Batteries have different sizes:
    # [25,62,100]
    listOfBatts = np.random.choice([25, 62, 100], numBattery, p=[sm, med, lg]).tolist()

    return listOfBatts

def charger_calculation(param_dict : dict):
    ev_current = get_single_param_with_name(param_dict, "EV_current")
    logger.info(f"Executing charger calculation with ev_current: {ev_current}")
    ret_val = {}
    ret_val["EV_voltage"] = ev_current * random.randint(1,3)
    return ret_val


if __name__ == "__main__":

    ##########  Registering  federate and configuring from JSON################
    simulator_configuration = get_simulator_configuration_from_environment()

    subscriptions_values = [
        SubscriptionDescription("PVInstallation", "EV_current", "A", h.HelicsDataType.DOUBLE)
    ]
    publictations_values = [
        PublicationDescription(True, "EConnection", "EV_voltage", "V", h.HelicsDataType.DOUBLE)
    ]

    logger.info(type(generate_subscriptions_from_value_descriptions))

    subscriptions_values = generate_subscriptions_from_value_descriptions(subscriptions_values, simulator_configuration)
    publication_values = generate_publications_from_value_descriptions(publictations_values, simulator_configuration)

    federate_executor = HelicsFederateExecutor(HelicValueFederateInformation(60, False, True, True, h.HelicsLogLevel.DEBUG,subscriptions_values, publication_values, charger_calculation), simulator_configuration)

    federate_executor.start_value_federate()