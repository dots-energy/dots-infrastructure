from typing import List

import esdl
from dots_infrastructure.DataClasses import CalculationService, ConnectedCalculationServcie, EsdlId

def get_model_esdl_object(esdl_id: EsdlId, energy_system: esdl.EnergySystem) -> esdl:
    if energy_system.id == esdl_id:
        return energy_system
    # Iterate over all contents of the EnergySystem
    for obj in energy_system.eAllContents():
        if hasattr(obj, "id") and obj.id == esdl_id:
            return obj
    raise IOError(f"ESDL_ID '{esdl_id}' not found in provided ESDL file")

def extract_calculation_service(calculation_services: List[CalculationService], esdl_obj) -> CalculationService:
    esdl_obj_type_name = type(esdl_obj).__name__
    calc_service = next(
        (
            calc_service
            for calc_service in calculation_services
            if calc_service.esdl_type == esdl_obj_type_name
        ),
        None,
    )
    
    return calc_service

def add_connected_esdl_object(service_info_dict: List[ConnectedCalculationServcie], calculation_services: List[CalculationService], esdl_obj: esdl):
    calc_service = extract_calculation_service(calculation_services, esdl_obj)

    if calc_service:
        connected_calculation_service = next((connected_calc_service for connected_calc_service in service_info_dict if connected_calc_service.esdl_type == calc_service.esdl_type), None)
        if connected_calculation_service:
            connected_calculation_service.connected_services.append(esdl_obj.id)
        else:
            service_info_dict.append(ConnectedCalculationServcie(calc_service.esdl_type, [esdl_obj.id]))

def add_calc_services_from_ports(
    calculation_services: List[CalculationService],
    connected_input_esdl_objects: List[ConnectedCalculationServcie],
    model_esdl_asset: esdl.EnergyAsset,
):
    for port in model_esdl_asset.port:
        if isinstance(port, esdl.InPort):
            for connected_port in port.connectedTo:
                connected_asset = connected_port.eContainer()
                add_connected_esdl_object(
                    connected_input_esdl_objects, calculation_services, connected_asset
                )

def add_calc_services_from_non_connected_objects(
    calculation_services: List[CalculationService],
    connected_input_esdl_objects: List[ConnectedCalculationServcie],
    energy_system: esdl,
):
    for esdl_obj in energy_system.eAllContents():
        if not isinstance(esdl_obj, esdl.EnergyAsset) and hasattr(esdl_obj, "id"):
            add_connected_esdl_object(
                connected_input_esdl_objects, calculation_services, esdl_obj
            )
    add_connected_esdl_object(connected_input_esdl_objects, calculation_services, energy_system)

def add_calc_services_from_all_objects(
    calculation_services: List[CalculationService],
    connected_input_esdl_objects: List[ConnectedCalculationServcie],
    energy_system: esdl.EnergySystem,
):
    for esdl_obj in energy_system.eAllContents():
        if hasattr(esdl_obj, "id"):
            add_connected_esdl_object(
                connected_input_esdl_objects, calculation_services, esdl_obj
            )

def get_connected_input_esdl_objects(
    esdl_id: EsdlId,
    calculation_services: List[CalculationService],
    energy_system: esdl.EnergySystem,
) -> List[ConnectedCalculationServcie]:
    model_esdl_obj = get_model_esdl_object(esdl_id, energy_system)

    connected_input_esdl_objects: List[ConnectedCalculationServcie] = []
    if isinstance(model_esdl_obj, esdl.EnergyAsset):
        add_calc_services_from_ports(
            calculation_services, connected_input_esdl_objects, model_esdl_obj
        )
        add_calc_services_from_non_connected_objects(
            calculation_services, connected_input_esdl_objects, energy_system
        )
    else:
        add_calc_services_from_all_objects(
            calculation_services, connected_input_esdl_objects, energy_system
        )
    return connected_input_esdl_objects