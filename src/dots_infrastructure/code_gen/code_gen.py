from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from dots_infrastructure.code_gen.code_meta_data import CalculationServiceMetaData

TEMPLATE_DIR = Path(__file__).parent / "templates"
JINJA_ENV = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

class CodeGenerator:
    base_output_path: Path

    def __init__(self, base_output_path: Path) -> None:
        self.base_output_path = base_output_path

    def render_template(self, template_path: Path, output_dir: Path, output_file: Path, **data):
        # jinja expects a string, representing a relative path with forward slashes
        template_path_str = str(template_path.relative_to(TEMPLATE_DIR)).replace("\\", "/")
        template = JINJA_ENV.get_template(template_path_str)
        JINJA_ENV.trim_blocks = True
        JINJA_ENV.lstrip_blocks = True

        output = template.render(**data)
        output_dir.mkdir(parents=True, exist_ok=True)
        with output_file.open(mode="w", encoding="utf-8") as output_file:
            output_file.write(output)

    def render_calculation_service(self, template_path: Path, json_data : str, output_dir: Path):

        dataset_meta_data: CalculationServiceMetaData = CalculationServiceMetaData.schema().loads(json_data)

        for calculation in dataset_meta_data.calculations:
            calculation.calculation_function_name = calculation.name.replace(" ", "_").replace("-", "_").replace(".", "_")

        output_file = output_dir / f"{dataset_meta_data.name}Base.py"

        self.render_template(
            template_path=template_path,
            output_dir=output_dir,
            output_file=output_file,
            calculations=dataset_meta_data.calculations,
            name=dataset_meta_data.name,
            esdl_type=dataset_meta_data.esdl_type
        )

    def render_documentation(self, template_path: Path, json_data : str, output_dir: Path):
        dataset_meta_data: CalculationServiceMetaData = CalculationServiceMetaData.schema().loads(json_data)

        output_file = output_dir / f"{dataset_meta_data.name}.md"

        self.render_template(
            template_path=template_path,
            output_dir=output_dir,
            output_file=output_file,
            calculations=dataset_meta_data.calculations,
            name=dataset_meta_data.name,
            esdl_type=dataset_meta_data.esdl_type,
            description=dataset_meta_data.description
        )

    def code_gen(self, input : str, output_dir : str):
        render_funcs = {
            "calculation_service": self.render_calculation_service,
            "cs_documentation": self.render_documentation,
        }

        # render attribute classes
        for template_name, render_func in render_funcs.items():
            for template_path in TEMPLATE_DIR.rglob(f"{template_name}.*.jinja"):
                output_dir = Path(output_dir)
                output_path = output_dir 
                output_path.parent.mkdir(parents=True, exist_ok=True)
                print(f"Generating file: {output_path}")
                render_func(template_path=template_path, json_data=input, output_dir=output_path)

