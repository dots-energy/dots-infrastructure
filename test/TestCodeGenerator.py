from pathlib import Path
import unittest
from unittest.mock import MagicMock, call

from dots_infrastructure.code_gen.code_gen import CodeGenerator, TEMPLATE_DIR
from dots_infrastructure.code_gen.code_meta_data import Calculation, CalculationServiceInputData, CalculationServiceOutputData, RelevantLink
import shutil

class TestLogicAddingCalculations(unittest.TestCase):
    def setUp(self):
        self.code_generator = CodeGenerator()
        self.code_generator.render_template = MagicMock()
        self.test_template_dir = TEMPLATE_DIR
        self.test_output_dir = Path("test_output_dir")
        self.test_documentation_dir = Path("test_documentation_dir")

    def tearDown(self):
        if self.test_output_dir.exists() and self.test_output_dir.is_dir():
            shutil.rmtree(self.test_output_dir)

    def test_exception_is_raised_when_invalid_data_type_is_provided(self):
        # Arrange
        with open("test_fault_code_gen_input.json", mode="r") as json_input:
            input_json = json_input.read()

        # Execute and Assert
        with self.assertRaises(ValueError):
            self.code_generator.render_calculation_service_base(self.test_template_dir, input_json, self.test_output_dir)

        with self.assertRaises(ValueError):
            self.code_generator.render_calculation_service(self.test_template_dir, input_json, self.test_output_dir)

        with self.assertRaises(ValueError):
            self.code_generator.render_output_dataclasses(self.test_template_dir, input_json, self.test_output_dir)

    def test_when_valid_input_is_supplied_render_template_cs_is_called_correctly(self):
        # Arrange
        with open("test_valid_input.json", mode="r") as json_input:
            input_json = json_input.read()

        # Execute
        self.code_generator.code_gen(input_json, self.test_output_dir, self.test_documentation_dir)

        # Assert
        expected_inputs = [
            CalculationServiceInputData("input1", "Weather", "input 1 description", "K", "STRING", "input1"),
        ]
        expected_outputs = [
            CalculationServiceOutputData("output1", "output 1 description", "W", "DOUBLE", python_data_type='float', python_name='output1')
        ]
        expected_calculations = [
            Calculation("test calculation", "test", 900, 0, expected_inputs, expected_outputs, calculation_function_name="test_calculation", calculation_output_class_name=None)
        ]
        expected_relevant_links = [
            RelevantLink("test link", "https://example.com/test", "this is a test link")
        ]
        expected_inputs_doc = [
            CalculationServiceInputData("input1", "Weather", "input 1 description", "K", "STRING"),
        ]
        expected_outputs_doc = [
            CalculationServiceOutputData("output1", "output 1 description", "W", "DOUBLE")
        ]
        expected_calculations_doc =[
            Calculation("test calculation", "test", 900, 0, expected_inputs_doc, expected_outputs_doc, calculation_function_name=None, calculation_output_class_name=None)
        ]
        expected_calculations_data =[
            Calculation("test calculation", "test", 900, 0, expected_inputs_doc, expected_outputs, calculation_function_name=None, calculation_output_class_name='TestCalculationOutput')
        ]
        calls = [
            call(template_path=self.test_template_dir / "calculation_service" / "calculation_service_base.py.jinja", output_dir=self.test_output_dir, output_file=Path("test_output_dir/test_base.py"), calculations=expected_calculations, name="TestBase", esdl_type="PVInstallation"),
            call(template_path=self.test_template_dir / "calculation_service" / "calculation_service.py.jinja", output_dir=self.test_output_dir, output_file=Path("test_output_dir/test.py"), calculations=expected_calculations, class_name="Test", base_class_name="TestBase", esdl_type="PVInstallation"),
            call(template_path=self.test_template_dir / "documentation" / "cs_documentation.md.jinja", output_dir=self.test_documentation_dir, output_file=Path("test_documentation_dir/test.md"), calculations=expected_calculations_doc, name="test", esdl_type="PVInstallation", description="this is a test description", relevant_links=expected_relevant_links),
            call(template_path=self.test_template_dir / "data_classes" / "cs_data_classes.py.jinja", output_dir=self.test_output_dir, output_file=Path("test_output_dir/test_dataclasses.py"), calculations=expected_calculations_data),
        ]
        self.code_generator.render_template.assert_has_calls(calls)

    def test_when_valid_input_is_supplied_render_template_dataclasses_is_called_correctly(self):
        # Arrange
        with open("test_valid_input.json", mode="r") as json_input:
            input_json = json_input.read()

        # Execute
        self.code_generator.render_output_dataclasses(self.test_template_dir, input_json, self.test_output_dir)

        # Assert
        expected_inputs = [
            CalculationServiceInputData("input1", "Weather", "input 1 description", "K", "STRING", None),
        ]
        expected_outputs = [
            CalculationServiceOutputData("output1", "output 1 description", "W", "DOUBLE", python_data_type='float', python_name='output1')
        ]
        expected_calculations = [
            Calculation("test calculation", "test", 900, 0, expected_inputs, expected_outputs, calculation_function_name=None, calculation_output_class_name='TestCalculationOutput')
        ]
        calls = [
            call(template_path=self.test_template_dir, output_dir=self.test_output_dir, output_file=Path("test_output_dir/test_dataclasses.py"), calculations=expected_calculations),
        ]
        self.code_generator.render_template.assert_has_calls(calls)

    def test_when_implementation_file_exists_render_template_cs_is_not_called(self):
        # Arrange
        with open("test_valid_input.json", mode="r") as json_input:
            input_json = json_input.read()

        # Pre-create the output file to simulate existing implementation
        output_file = self.test_output_dir / "test.py"
        self.test_output_dir.mkdir(parents=True, exist_ok=True)
        output_file.touch()

        # Execute
        self.code_generator.render_calculation_service(self.test_template_dir, input_json, self.test_output_dir)

        # Assert
        self.code_generator.render_template.assert_not_called()

if __name__ == '__main__':
    unittest.main()