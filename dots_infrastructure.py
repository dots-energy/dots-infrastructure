import os
from typing import List
import helics as h
import logging
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

@dataclass
class CalculationServiceInput:
    esdl_asset_type : str
    input_name : str
    input_esdl_id : str
    input_unit : str
    input_type : h.HelicsDataType
    simulator_esdl_id : str
    helics_input : h.HelicsInput = None

@dataclass 
class CalculationServiceOutput:
    global_flag : bool
    esdl_asset_type : str
    output_name : str
    output_esdl_id : str
    output_type : h.HelicsDataType
    output_unit : str
    helics_publication : h.HelicsPublication = None

@dataclass
class HelicValueFederateInformation:
    time_period_in_seconds : float
    uninterruptible : bool
    wait_for_current_time_update : bool
    terminate_on_error : bool
    log_level : int
    inputs : List[CalculationServiceInput]
    outputs : List[CalculationServiceOutput]
    calculation_function : any

@dataclass
class SubscriptionDescription:
    esdl_type : str
    input_name : str
    input_unit : str
    input_type : h.HelicsDataType

@dataclass
class PublicationDescription:
    global_flag : bool
    esdl_type : str
    input_name : str
    input_unit : str
    data_type : h.HelicsDataType

@dataclass
class SimulatorConfiguration:
    esdl_type : str
    connected_services : dict
    esdl_ids : List[str]
    model_id : str
    broker_ip : str
    broker_port : int

def get_simulator_configuration_from_environment() -> SimulatorConfiguration:
    esdl_ids = os.getenv("esdl_ids", "e1b3dc89-cee8-4f8e-81ce-a0cb6726c17e;f006d594-0743-4de5-a589-a6c2350898da").split(";")
    connected_services_json = os.getenv("connected_services", '{"e1b3dc89-cee8-4f8e-81ce-a0cb6726c17e":[{"esdl_type":"PVInstallation","connected_services":["1830a516-fae5-4cc7-99bd-6e9a5d175a80"]}],"f006d594-0743-4de5-a589-a6c2350898da":[{"esdl_type":"PVInstallation","connected_services":["176af591-6d9d-4751-bb0f-fac7e99b1c3d","b8766109-5328-416f-9991-e81a5cada8a6"]}]}')
    connected_services = json.loads(connected_services_json)
    esdl_type = os.getenv("esdl_type", "test-type")
    model_id = os.getenv("model_id", "test-id")
    broker_ip = os.getenv("broker_ip", "127.0.0.1")
    broker_port = int(os.getenv("broker_port", "30000"))
    return SimulatorConfiguration(esdl_type, connected_services, esdl_ids, model_id, broker_ip, broker_port)

def generate_subscriptions_from_value_descriptions(value_descriptions : List[SubscriptionDescription], simulator_configuration : SimulatorConfiguration) -> List[CalculationServiceInput]:
    ret_val = []
    for value_description in value_descriptions:
        for simulator_esdl_id in simulator_configuration.esdl_ids:
            connected_esdl_assets = simulator_configuration.connected_services[simulator_esdl_id]
            for connected_esdl_asset in connected_esdl_assets:
                if connected_esdl_asset["esdl_type"] == value_description.esdl_type:
                    for esdl_id in connected_esdl_asset["connected_services"]:
                        ret_val.append(CalculationServiceInput(value_description.esdl_type, value_description.input_name, esdl_id, value_description.input_unit, value_description.input_type, simulator_esdl_id))
    if len(ret_val) == 0:
        logger.warning("Subscription list is empty!")
    return ret_val

def generate_publications_from_value_descriptions(value_descriptions : List[PublicationDescription], simulator_configuration : SimulatorConfiguration) -> List[CalculationServiceOutput]:
    ret_val = []
    for value_description in value_descriptions:
        for esdl_id in simulator_configuration.esdl_ids:
            ret_val.append(CalculationServiceOutput(value_description.global_flag, value_description.esdl_type, value_description.input_name, esdl_id, value_description.data_type, value_description.input_unit))
    return ret_val

def get_single_param_with_name(param_dict : dict, name : str):
    for key in param_dict.keys():
        if name in key:
            return param_dict[key]

def get_vector_param_with_name(param_dict : dict, name : str):
    return [value for key, value in param_dict.items() if name in key]

class HelicsFederateExecutor:

    def __init__(self, info : HelicValueFederateInformation, simulator_configuration : SimulatorConfiguration):

        self.input_dict : dict[str, List[CalculationServiceInput]] = {}
        self.output_dict : dict[str, List[CalculationServiceOutput]] = {}
        self.simulator_configuration = simulator_configuration

        federate_info = self.init_value_federate(info)
        value_federate = h.helicsCreateValueFederate(simulator_configuration.model_id, federate_info)

        self.init_inputs(info, value_federate)
        self.init_outputs(info, value_federate)
        self.calculation_function = info.calculation_function

        self.value_federate = value_federate

    def init_outputs(self, info : HelicValueFederateInformation, value_federate : h.HelicsValueFederate):

        for output in info.outputs:
            key = f'{output.esdl_asset_type}/{output.output_name}/{output.output_esdl_id}'
            if output.global_flag:
                pub = h.helicsFederateRegisterGlobalPublication(value_federate, key, output.output_type, output.output_unit)
            else:
                pub = h.helicsFederateRegisterPublication(value_federate, key, output.output_type, output.output_unit)
            output.helics_publication = pub
            if output.output_esdl_id in self.output_dict:
                self.output_dict[output.output_esdl_id].append(output)
            else:
                self.output_dict[output.output_esdl_id] = [output]

    def init_inputs(self, info : HelicValueFederateInformation, value_federate : h.HelicsValueFederate):
        for input in info.inputs:
            sub_key = f'{input.esdl_asset_type}/{input.input_name}/{input.input_esdl_id}'
            logger.info(f"Adding Subscription {sub_key} for esdl id: {input.simulator_esdl_id} ")
            sub = h.helicsFederateRegisterSubscription(value_federate, sub_key, input.input_unit)
            input.helics_input = sub

            if input.input_esdl_id in self.input_dict:
                self.input_dict[input.simulator_esdl_id].append(input)
            else:
                self.input_dict[input.simulator_esdl_id] = [input]

    def init_value_federate(self, info : HelicValueFederateInformation):
        federate_info = h.helicsCreateFederateInfo()
        h.helicsFederateInfoSetBroker(federate_info, self.simulator_configuration.broker_ip)
        h.helicsFederateInfoSetBrokerPort(federate_info, self.simulator_configuration.broker_port)
        h.helicsFederateInfoSetTimeProperty(federate_info, h.HelicsProperty.TIME_PERIOD, info.time_period_in_seconds)
        h.helicsFederateInfoSetFlagOption(federate_info, h.HelicsFederateFlag.UNINTERRUPTIBLE, info.uninterruptible)
        h.helicsFederateInfoSetFlagOption(federate_info, h.HelicsFederateFlag.WAIT_FOR_CURRENT_TIME_UPDATE, info.wait_for_current_time_update)
        h.helicsFederateInfoSetFlagOption(federate_info, h.HelicsFlag.TERMINATE_ON_ERROR, info.terminate_on_error)
        h.helicsFederateInfoSetCoreType(federate_info, h.HelicsCoreType.ZMQ)
        h.helicsFederateInfoSetIntegerProperty(federate_info, h.HelicsProperty.INT_LOG_LEVEL, info.log_level)
        return federate_info

    def get_helics_value(self, helics_sub : CalculationServiceInput):
        logger.debug(f"Getting value for subscription: {helics_sub.input_name} with type: {helics_sub.input_type}")
        input_type = helics_sub.input_type
        sub = helics_sub.helics_input
        if input_type == h.HelicsDataType.BOOLEAN:
            return h.helicsInputGetBoolean(sub)
        elif input_type == h.HelicsDataType.COMPLEX_VECTOR:
            return h.helicsInputGetComplexVector(sub)
        elif input_type == h.HelicsDataType.DOUBLE:
            return h.helicsInputGetDouble(sub)
        elif input_type == h.HelicsDataType.COMPLEX:
            return h.helicsInputGetComplex(sub)
        elif input_type == h.HelicsDataType.INT:
            return h.helicsInputGetInteger(sub)
        elif input_type == h.HelicsDataType.JSON:
            return h.helicsInputGetString(sub)
        elif input_type == h.HelicsDataType.NAMED_POINT:
            return h.helicsInputGetNamedPoint(sub)
        elif input_type == h.HelicsDataType.STRING:
            return h.helicsInputGetString(sub)
        elif input_type == h.HelicsDataType.RAW:
            return h.helicsInputGetRawValue(sub)
        elif input_type == h.HelicsDataType.TIME:
            return h.helicsInputGetTime(sub)
        elif input_type == h.HelicsDataType.VECTOR:
            return h.helicsInputGetVector(sub)
        elif input_type == h.HelicsDataType.ANY:
            return h.helicsInputGetBytes(sub)
        else:
            raise ValueError("Unsupported Helics Data Type")
        
    def publish_helics_value(self, helics_output : CalculationServiceOutput, value):
        logger.debug(f"Publishing value: {value} for publication: {helics_output.output_name} with type: {helics_output.output_type}")
        pub = helics_output.helics_publication
        output_type = helics_output.output_type
        if output_type == h.HelicsDataType.BOOLEAN:
            h.helicsPublicationPublishBoolean(pub, value)
        elif output_type == h.HelicsDataType.COMPLEX_VECTOR:
            h.helicsPublicationPublishComplexVector(pub, value)
        elif output_type == h.HelicsDataType.DOUBLE:
            h.helicsPublicationPublishDouble(pub, value)
        elif output_type == h.HelicsDataType.COMPLEX:            
            h.helicsPublicationPublishComplex(pub, value)
        elif output_type == h.HelicsDataType.INT:
            h.helicsPublicationPublishInteger(pub, value)
        elif output_type == h.HelicsDataType.JSON:
            h.helicsPublicationPublishString(pub, value)
        elif output_type == h.HelicsDataType.NAMED_POINT:
            h.helicsPublicationPublishNamedPoint(pub, value)
        elif output_type == h.HelicsDataType.STRING:
            h.helicsPublicationPublishString(pub, value)
        elif output_type == h.HelicsDataType.RAW:
            h.helicsPublicationPublishRaw(pub, value)
        elif output_type == h.HelicsDataType.TIME:
            h.helicsPublicationPublishTime(pub, value)
        elif output_type == h.HelicsDataType.VECTOR:
            h.helicsPublicationPublishVector(pub, value)
        elif output_type == h.HelicsDataType.ANY:
            h.helicsPublicationPublishBytes(pub, value)
        else:
            raise ValueError("Unsupported Helics Data Type")

    def start_value_federate(self):
        h.helicsFederateEnterExecutingMode(self.value_federate)
    
        logger.info("Entered HELICS execution mode")
    
        hours = 24 * 7 # replace by simulation parameters
        total_interval = int(60 * 60 * hours) # replace by simulation parameters
        update_interval = int(h.helicsFederateGetTimeProperty(self.value_federate, h.HELICS_PROPERTY_TIME_PERIOD))
        grantedtime = 0
    
        # As long as granted time is in the time range to be simulated...
        while grantedtime < total_interval:
            requested_time = grantedtime + update_interval
            grantedtime = h.helicsFederateRequestTime(self.value_federate, requested_time)

            for esdl_id in self.simulator_configuration.esdl_ids:
                calculation_params = {}
                if esdl_id in self.input_dict:
                    inputs = self.input_dict[esdl_id]
                    for helics_input in inputs:
                        calculation_params[helics_input.input_name] = self.get_helics_value(helics_input)
                logger.info(f"Executing calculation for esdl_id {esdl_id} at time {grantedtime}")
                pub_values = self.calculation_function(calculation_params)

                outputs = self.output_dict[esdl_id]
                for output in outputs:
                    value_to_publish = pub_values[output.output_name]
                    self.publish_helics_value(output, value_to_publish)


