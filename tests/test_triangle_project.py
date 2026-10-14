import unittest
from unittest.mock import Mock, patch

from src.calculation.triangle_validator import TriangleCalculator
from src.controller.controller import Controller
from src.database.triangle_database import TriangleDatabase
from src.external_dependency.external_service import ExternalDependency
from src.user_interface.user_interface import ConsoleUserInput, UserInputInterface


class TriangleProjectIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.database = TriangleDatabase(":memory:")
        self.addCleanup(self.database.close)
        self.user_interface = Mock(spec=UserInputInterface)
        self.external_dependency = Mock(spec=ExternalDependency)
        self.external_dependency.send_result.return_value = True
        self.calculator = Mock(spec=TriangleCalculator)
        self.controller = Controller(
            calculator=self.calculator,
            database=self.database,
            user_interface=self.user_interface,
            external_dependency=self.external_dependency,
        )

    def test_new_result_is_calculated_saved_and_sent(self):
        self.user_interface.get_triangle_data.return_value = ["3", "4", "5"]
        calculated_result = ("разносторонний", [(10, 20), (30, 20), (20, 40)], "")
        self.calculator.calculate.return_value = calculated_result

        result = self.controller.run()

        self.calculator.calculate.assert_called_once_with(["3", "4", "5"])
        self.assertEqual(self.database.get_record(3, 4, 5)["triangle_type"], "разносторонний")
        self.external_dependency.send_result.assert_called_once_with(result)
        self.assertIn("разносторонний", result)

    def test_cached_result_skips_calculation_and_is_sent(self):
        self.database.add_record(3, 4, 5, "разносторонний")
        self.user_interface.get_triangle_data.return_value = ["3", "4", "5"]

        result = self.controller.run()

        self.calculator.calculate.assert_not_called()
        self.assertEqual(result, "Тип: разносторонний")
        self.external_dependency.send_result.assert_called_once_with(result)

    def test_deleted_record_is_recalculated_and_saved_again(self):
        self.database.add_record(3, 4, 5, "устаревшее значение")
        self.database.delete_record(3, 4, 5)
        self.user_interface.get_triangle_data.return_value = ["3", "4", "5"]
        self.calculator.calculate.return_value = ("разносторонний", [(10, 20), (30, 20), (20, 40)], "")

        self.controller.run()

        self.calculator.calculate.assert_called_once_with(["3", "4", "5"])
        self.assertEqual(self.database.get_record(3, 4, 5)["triangle_type"], "разносторонний")
        self.external_dependency.send_result.assert_called_once()

    def test_invalid_number_of_values_is_reported_without_calculation(self):
        self.user_interface.get_triangle_data.return_value = ["3", "4"]

        result = self.controller.run()

        self.assertEqual(result, "Ошибка: Некорректное число входных значений.")
        self.calculator.calculate.assert_not_called()
        self.external_dependency.send_result.assert_called_once_with(result)


class TriangleComponentTests(unittest.TestCase):
    def test_console_input_reads_three_values_using_mocked_input(self):
        user_interface = ConsoleUserInput()
        with patch("builtins.input", side_effect=[" 3 ", "4", " 5 "]) as mocked_input:
            values = user_interface.get_triangle_data()

        self.assertEqual(values, ["3", "4", "5"])
        self.assertEqual(mocked_input.call_count, 3)

    def test_database_delete_removes_existing_record(self):
        database = TriangleDatabase(":memory:")
        self.addCleanup(database.close)
        database.add_record(3, 4, 5, "разносторонний")

        database.delete_record(3, 4, 5)

        self.assertIsNone(database.get_record(3, 4, 5))


if __name__ == "__main__":
    unittest.main()
