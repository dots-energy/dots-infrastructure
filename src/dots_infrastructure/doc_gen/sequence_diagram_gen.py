import os
import argparse
from dataclasses import dataclass
from typing import List, Tuple
from dots_infrastructure.code_gen.code_meta_data import CalculationServiceInputData, CalculationServiceMetaData, Calculation, CalculationServiceOutputData

@dataclass
class SequenceDiagramMessage:
    sender : str
    reciever : str
    message : str

@dataclass 
class SequenceDiagramParticipant:
    name : str
    esdl_type : str

@dataclass
class CalculationNode:
    origin_type : str
    calculation_name : str
    inputs : List[CalculationServiceInputData]
    outputs : List[CalculationServiceOutputData]

def generate_messages(calculations : List[CalculationNode]) -> List[SequenceDiagramMessage]:
    messages = []
    
    calculation_roots = [calculation for calculation in calculations if len(calculation.inputs) == 0]
    for calculation_root in calculation_roots:
        new_msg = SequenceDiagramMessage(sender=calculation_root.origin_type, reciever=calculation_root.origin_type, message=calculation_root.calculation_name)
        messages.append(new_msg)

    while len(calculation_roots) > 0:
        for calculation_root in calculation_roots:
            calculations.remove(calculation_root)
            calculation_children = [calculation for calculation in calculations if calculation_root.origin_type in [input.esdl_type for input in calculation.inputs]]
            for calculation_child in calculation_children:
                inputs_to_remove = []
                for input in calculation_child.inputs:
                    if input.esdl_type == calculation_root.origin_type and input.name in [output.name for output in calculation_root.outputs]:
                        new_msg = SequenceDiagramMessage(sender=calculation_root.origin_type, reciever=calculation_child.origin_type, message=input.name)
                        if new_msg not in messages:
                            messages.append(new_msg)
                        inputs_to_remove.append(input)
                for input_to_remove in inputs_to_remove:
                    calculation_child.inputs.remove(input_to_remove)
                if len(calculation_child.inputs) == 0:
                    messages.append(SequenceDiagramMessage(sender=calculation_child.origin_type, reciever=calculation_child.origin_type, message=f"Execute {calculation_child.calculation_name}"))
        calculation_roots = [calculation for calculation in calculations if len(calculation.inputs) == 0]

    return messages


def parse_inputs(input_folder : str, output_file : str):
    participants, all_calculations = extract_relevant_data(input_folder)
    messages = generate_messages(all_calculations)
    write_output_file(output_file, participants, messages)

def write_output_file(output_file : str, participants : List[SequenceDiagramParticipant], messages : List[SequenceDiagramMessage]):
    plantuml_lines = ["@startuml"]
    for participant in participants:
        plantuml_lines.append(f"participant {participant.esdl_type} [")
        plantuml_lines.append(f"= {participant.name}")
        plantuml_lines.append(f"----")
        plantuml_lines.append(participant.esdl_type)
        plantuml_lines.append(f"]")

    for message in messages:
        plantuml_lines.append(f"{message.sender} -> {message.reciever} : {message.message}")

    plantuml_lines.append("@enduml")
    with open(output_file, 'w') as f:
        f.write("\n".join(plantuml_lines))

def extract_relevant_data(input_folder) -> Tuple[List[SequenceDiagramParticipant], List[Calculation]]:
    participants = []
    all_calculations = []
    for file in os.listdir(input_folder):
        if file.endswith(".json"):
            file_path = os.path.join(input_folder, file)
            with open(file_path, 'r') as f:
                print("Processing file:", file)
                dataset_meta_data : CalculationServiceMetaData = CalculationServiceMetaData.schema().loads(f.read())
                participants.append(SequenceDiagramParticipant(name=dataset_meta_data.name, esdl_type=dataset_meta_data.esdl_type))
                all_calculations.extend([CalculationNode(dataset_meta_data.esdl_type, calculation.name, calculation.inputs, calculation.outputs) for calculation in dataset_meta_data.calculations])
        else:
            print("Skipping non-JSON file:", file)
    return participants,all_calculations

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_folder", help = "The folder containing all the json configuration files of the calculation services", required=True)
    parser.add_argument("-o", "--output_file", help = "The name of the output plantuml file", required=True)
    args = parser.parse_args()
    input_folder = args.input_folder
    output_file = args.output_file

    if os.path.exists(input_folder) and os.path.isdir(input_folder):
        parse_inputs(input_folder, output_file)
    else:
        print("Input folder does not exist or is not a directory.")


if __name__ == "__main__":
    exit(main())