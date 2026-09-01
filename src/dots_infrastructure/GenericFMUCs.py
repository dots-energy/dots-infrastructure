from datetime import datetime
import json
from pathlib import Path
import helics as h
from dots_infrastructure.DataClasses import FMUVariableCollections, FmuInputVariable, FmuMetaData, FmuOutputVariable, TimeStepInformation, EsdlId, HelicsCalculationInformation, PublicationDescription, SubscriptionDescription
from dots_infrastructure.HelicsFederateHelpers import HelicsSimulationExecutor
from dots_infrastructure import CalculationServiceHelperFunctions
from esdl import EnergySystem, Item
from fmpy.model_description import ModelVariable, read_model_description
from fmpy.fmi2 import FMU2Slave
from fmpy import extract
from typing import List


FMU_TO_HELICS_TYPE_MAPPING = {
    'Real' : h.HelicsDataType.DOUBLE,
    'Float32' : h.HelicsDataType.DOUBLE,
    'Float64' : h.HelicsDataType.DOUBLE,
    'Integer' : h.HelicsDataType.INT,
    'Int8' : h.HelicsDataType.INT,
    'UInt8' : h.HelicsDataType.INT,
    'Int16' : h.HelicsDataType.INT,
    'UInt16' : h.HelicsDataType.INT,
    'Int32' : h.HelicsDataType.INT,
    'UInt32' : h.HelicsDataType.INT,
    'Int64': h.HelicsDataType.INT,
    'Enumeration' : h.HelicsDataType.INT,
    'Boolean' : h.HelicsDataType.BOOLEAN,
    'String' : h.HelicsDataType.STRING,
    'Binary' : h.HelicsDataType.BOOLEAN,
    'Clock' : h.HelicsDataType.STRING
}

class FmuCalculationService(HelicsSimulationExecutor):

    def __init__(self, fmu_file_names : list[Path], input_mapping : list[FmuInputVariable], output_mapping : list[FmuOutputVariable]):
        super().__init__()
        self.amount_of_calculations = 1
        self.fmu_paths : List[Path] = fmu_file_names
        self.esdl_obj_mapping : dict[EsdlId, Item] = {}
        self.fmu_meta_data_mapping : dict[str, FmuMetaData] = {}
        self.input_variables : List[FmuInputVariable] = input_mapping
        self.output_variables : List[FmuOutputVariable] = output_mapping


    def init_fmu_metadata(self) -> dict[str, FmuMetaData]:
        fmu_metadata_list : dict[str, FmuMetaData] = {}
        for path in self.fmu_paths:
            model_description = read_model_description(str(path))
            parameter_variables = [var for var in model_description.modelVariables if var.causality == "parameter"]
            input_variables = [var for var in model_description.modelVariables if var.causality == "input"]
            output_variables = [var for var in model_description.modelVariables if var.causality == "output"]
            fmu_variable_collections = FMUVariableCollections(parameter_variables, input_variables, output_variables, float(model_description.defaultExperiment.stepSize))
            fmu_metadata_list[path.name] = FmuMetaData(path, model_description, fmu_variable_collections)

        return fmu_metadata_list


    def init_fmu(self, fmu : FMU2Slave, esdl_obj : Item, fmu_parameters : List[ModelVariable]):
        fmu.instantiate()
        fmu.setupExperiment(startTime=0)
        fmu.enterInitializationMode()
        json_string = esdl_obj.description
        parameter_details : dict = json.loads(json_string)
        self.set_values_on_fmu(fmu, fmu_parameters, parameter_details)

        fmu.exitInitializationMode()


    def set_values_on_fmu(self, fmu : FMU2Slave, parameter_collection : List[ModelVariable], parameter_values_to_set : dict):
        for parameter in parameter_collection:
            parameter_value = parameter_values_to_set.get(parameter.name, None)
            if parameter_value is not None and FMU_TO_HELICS_TYPE_MAPPING[parameter.type] == h.HelicsDataType.DOUBLE:
                fmu.setReal([parameter.valueReference], [parameter_value])
            elif parameter_value is not None and FMU_TO_HELICS_TYPE_MAPPING[parameter.type] == h.HelicsDataType.INT:
                fmu.setInteger([parameter.valueReference], [parameter_value])
            elif parameter_value is not None and FMU_TO_HELICS_TYPE_MAPPING[parameter.type] == h.HelicsDataType.BOOLEAN:
                fmu.setBoolean([parameter.valueReference], [parameter_value])
            elif parameter_value is not None and FMU_TO_HELICS_TYPE_MAPPING[parameter.type] == h.HelicsDataType.STRING:
                fmu.setString([parameter.valueReference], [parameter_value])


    def init_esdl_id_fmu_mapping(self, fmu_meta_data_mapping : dict[str, FmuMetaData]):
        self.esld_id_fmu_mapping : dict[EsdlId, FMU2Slave] = {}

        for i, esdl_id in enumerate(self.simulator_configuration.esdl_ids):
            fmu_model_name = self.esdl_obj_mapping[esdl_id].name
            fmu_meta_data = fmu_meta_data_mapping[fmu_model_name]
            fmu = FMU2Slave(guid=fmu_meta_data.model_description.guid,
                unzipDirectory=extract(fmu_meta_data.path),
                modelIdentifier=fmu_meta_data.model_description.coSimulation.modelIdentifier,
                instanceName=f'{fmu_model_name}_instance{i}')

            self.init_fmu(fmu, self.esdl_obj_mapping[esdl_id], fmu_meta_data.variable_collections.parameter_variables)
            self.esld_id_fmu_mapping[esdl_id] = fmu


    def get_all_esdl_objects(self, energy_system : EnergySystem):
        for esdl_obj in energy_system.eAllContents():
            if hasattr(esdl_obj, "id") and esdl_obj.id in self.simulator_configuration.esdl_ids:
                self.esdl_obj_mapping[esdl_obj.id] = esdl_obj


    def init_calculation(self, fmu_variable_collections : FMUVariableCollections):
        fmu_calculation_inputs = []
        fmu_calculation_outputs = []
        # Specify in dots infrastructure
        for input_variable in fmu_variable_collections.input_variables:
            fmu_input_variable = next(fmu_input_variable for fmu_input_variable in self.input_variables if fmu_input_variable.fmu_input_name == input_variable.name)
            input_unit = fmu_input_variable.calculation_service_input_unit if fmu_input_variable.calculation_service_input_unit != "" else input_variable.unit
            fmu_calculation_inputs.append(
                SubscriptionDescription(esdl_type=fmu_input_variable.esdl_type_input, 
                                        input_name=fmu_input_variable.calculation_service_input_name, 
                                        input_unit=input_unit, 
                                        input_type=FMU_TO_HELICS_TYPE_MAPPING[input_variable.type])
            )

        publication_mapping : dict[str, List[ModelVariable]] = {}
        for output_variable in self.output_variables:
            fmu_output_variable = next(fmu_output_variable for fmu_output_variable in fmu_variable_collections.output_variables if fmu_output_variable.name == output_variable.fmu_output_name)

            if output_variable.calculation_service_output_name not in publication_mapping:
                publication_mapping[output_variable.calculation_service_output_name] = []

            publication_mapping[output_variable.calculation_service_output_name].append(fmu_output_variable)

        for calculation_service_output_name in publication_mapping.keys():
            if len(publication_mapping[calculation_service_output_name]) > 1:
                output_variable = next(output_variable for output_variable in self.output_variables if output_variable.calculation_service_output_name == calculation_service_output_name)
                fmu_calculation_outputs.append(
                    PublicationDescription(global_flag=True,
                                            esdl_type=f"{self.simulator_configuration.esdl_type}", 
                                            output_name=calculation_service_output_name, 
                                            output_unit=f"{output_variable.calculation_service_output_unit}", 
                                            data_type=h.HelicsDataType.VECTOR),
                )
            else:
                fmu_calculation_outputs.append(
                    PublicationDescription(global_flag=True,
                                            esdl_type=f"{self.simulator_configuration.esdl_type}", 
                                            output_name=calculation_service_output_name, 
                                            output_unit=f"{output_variable.calculation_service_output_unit}", 
                                            data_type=FMU_TO_HELICS_TYPE_MAPPING[publication_mapping[calculation_service_output_name][0].type]),
                )

        fmu_calculation_information = HelicsCalculationInformation(
            time_period_in_seconds=fmu_variable_collections.step_size,
            offset=0, 
            uninterruptible=False, 
            wait_for_current_time_update=False, 
            terminate_on_error=True, 
            calculation_name=f"fmu_step_{self.simulator_configuration.esdl_type}", 
            inputs=fmu_calculation_inputs, 
            outputs=fmu_calculation_outputs, 
            calculation_function=self.fmu_calculation_step
        )
        self.add_calculation(fmu_calculation_information)


    def extract_variable_values(self, fmu_slave : FMU2Slave, variable_collection : List[ModelVariable]):
        ret_val = {}
        for variable in variable_collection:
            if FMU_TO_HELICS_TYPE_MAPPING[variable.type] == h.HelicsDataType.DOUBLE:
                ret_val[variable.name] = fmu_slave.getReal([variable.valueReference])[0]
            elif FMU_TO_HELICS_TYPE_MAPPING[variable.type] == h.HelicsDataType.INT:
                ret_val[variable.name] = fmu_slave.getInteger([variable.valueReference])[0]
            elif FMU_TO_HELICS_TYPE_MAPPING[variable.type] == h.HelicsDataType.BOOLEAN:
                ret_val[variable.name] = fmu_slave.getBoolean([variable.valueReference])[0]
            elif FMU_TO_HELICS_TYPE_MAPPING[variable.type] == h.HelicsDataType.STRING:
                ret_val[variable.name] = fmu_slave.getString([variable.valueReference])[0]
        return ret_val


    def _assert_inputs_and_outputs_are_equal_accross_fmus(self):
        meta_datas = list(self.fmu_meta_data_mapping.values())

        for i in range(len(meta_datas)):
            for j in range(i, len(meta_datas)):
                meta_data_i = meta_datas[i]
                meta_data_j = meta_datas[j]
                meta_data_j_input_names = [input_var.name for input_var in meta_data_j.variable_collections.input_variables]
                meta_data_j_output_names = [output_var.name for output_var in meta_data_j.variable_collections.output_variables]
                all_ins = all(input_var.name in meta_data_j_input_names for input_var in meta_data_i.variable_collections.input_variables)
                all_outs = all(input_var.name in meta_data_j_output_names for input_var in meta_data_i.variable_collections.output_variables)
                if not all_ins and all_outs:
                    raise ValueError("Not all fmus share the same input and output variables")


    def init_calculation_service(self, energy_system: EnergySystem):
        self.get_all_esdl_objects(energy_system)

        self.fmu_meta_data_mapping = self.init_fmu_metadata()

        self.init_esdl_id_fmu_mapping(self.fmu_meta_data_mapping)
        self._assert_inputs_and_outputs_are_equal_accross_fmus()
        self.init_calculation(self.fmu_meta_data_mapping[self.fmu_paths[0].name].variable_collections)


    def prepare_input_dict(self, param_dict : dict, fmu_inputs : List[ModelVariable]) -> dict:
        ret_val = {}
        for fmu_input in fmu_inputs:
            value_mapping = next(value for value in self.input_variables if value.fmu_input_name == fmu_input.name)
            ret_val[fmu_input.name] = CalculationServiceHelperFunctions.get_single_param_with_name(param_dict, value_mapping.calculation_service_input_name)

        return ret_val


    def fmu_calculation_step(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        cur_time_delta = simulation_time - self.simulator_configuration.start_time
        cur_time_in_seconds = cur_time_delta.total_seconds()
        variable_collections = self.fmu_meta_data_mapping[self.esdl_obj_mapping[esdl_id].name].variable_collections

        fmu_to_step_with = self.esld_id_fmu_mapping[esdl_id]

        param_dict_converted = self.prepare_input_dict(param_dict, variable_collections.input_variables)
        self.set_values_on_fmu(fmu_to_step_with, variable_collections.input_variables, param_dict_converted)

        fmu_to_step_with.doStep(currentCommunicationPoint=cur_time_in_seconds, communicationStepSize=variable_collections.step_size)

        ret_val = self.extract_variable_values(fmu_to_step_with, variable_collections.output_variables)

        return ret_val
