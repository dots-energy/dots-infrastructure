import random
import helics as h
import logging
from dots_infrastructure import PublicationDescription, HelicsValueFederateExecutor, HelicsMessageFederateInformation, HelicValueFederateInformation, HelicsEsdlMessageFederateExecutor, generate_publications_from_value_descriptions, generate_subscriptions_from_value_descriptions, get_simulator_configuration_from_environment


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

def battery_calculation(param_dict : dict):
    ret_val = {}
    ret_val["EV_current"] = 0.25 * random.randint(1,3)
    return ret_val


if __name__ == "__main__":

    ##########  Registering  federate and configuring from JSON################
    simulator_configuration = get_simulator_configuration_from_environment()

    publictations_values = [
        PublicationDescription(True, "PVInstallation", "EV_current", "A", h.HelicsDataType.DOUBLE)
    ]

    logger.info(type(generate_subscriptions_from_value_descriptions))

    subscriptions_values = []
    publication_values = generate_publications_from_value_descriptions(publictations_values, simulator_configuration)

    esdl_message_federate = HelicsEsdlMessageFederateExecutor(simulator_configuration, HelicsMessageFederateInformation(60, False, False, True, h.HelicsLogLevel.DEBUG, f'{simulator_configuration.model_id}/esdl'))

    energy_system = esdl_message_federate.wait_for_esdl_file()

    federate_executor = HelicsValueFederateExecutor(HelicValueFederateInformation(30, False, False, True, h.HelicsLogLevel.DEBUG,subscriptions_values, publication_values, battery_calculation), simulator_configuration)

    federate_executor.start_value_federate()