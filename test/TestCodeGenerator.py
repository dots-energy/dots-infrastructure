import unittest

from dots_infrastructure.code_gen.code_gen import CodeGenerator


class TestLogicAddingCalculations(unittest.TestCase):
    def setUp(self):
        self.code_generator = CodeGenerator()
        
    def test_exception_is_raised_when_invalid_data_type_is_provided(self):
        pass