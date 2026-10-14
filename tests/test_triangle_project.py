import unittest
from typing import List

from src.calculation.triangle_validator import TriangleCalculator
from src.controller.controller import Controller
from src.database.triangle_database import TriangleDatabase
from src.external_dependency.external_service import MockExternalDependency
from src.user_interface.user_interface import UserInputInterface


class FakeUserInput(UserInputInterface):
    def __init__(self, values: List[str]):
        self.values = values

    def get_triangle_data(self) -> List[str]:
        return list(self.values)


class TriangleProjectTests(unittest.TestCase):
    def test_calculator_recognizes_equilateral_triangle(self):
        calculator = TriangleCalculator()
        triangle_type, vertices, error = calculator.calculate(["3", "3", "3"])

        self.assertEqual(triangle_type, "равносторонний")
        self.assertEqual(error, "")
        self.assertEqual(len(vertices), 3)

    def test_database_add_and_get_record(self):
        database = TriangleDatabase(":memory:")
        database.add_record(3, 4, 5, "разносторонний", "")

        record = database.get_record(3, 4, 5)

        self.assertIsNotNone(record)
        self.assertEqual(record["triangle_type"], "разносторонний")
        database.close()

    def test_controller_uses_database_cache_for_existing_triangle(self):
        database = TriangleDatabase(":memory:")
        database.add_record(3, 4, 5, "разносторонний", "")
        external = MockExternalDependency()
        controller = Controller(
            database=database,
            user_interface=FakeUserInput(["3", "4", "5"]),
            external_dependency=external,
        )

        result = controller.run()

        self.assertIn("Тип: разносторонний", result)
        self.assertEqual(len(external.sent_messages), 1)
        database.close()

    def test_controller_computes_new_triangle_and_saves_result(self):
        database = TriangleDatabase(":memory:")
        external = MockExternalDependency()
        controller = Controller(
            database=database,
            user_interface=FakeUserInput(["5", "5", "5"]),
            external_dependency=external,
        )

        result = controller.run()
        record = database.get_record(5, 5, 5)

        self.assertIn("Тип: равносторонний", result)
        self.assertIsNotNone(record)
        self.assertEqual(record["triangle_type"], "равносторонний")
        self.assertEqual(len(external.sent_messages), 1)
        database.close()

    def test_controller_handles_non_triangle_input(self):
        database = TriangleDatabase(":memory:")
        external = MockExternalDependency()
        controller = Controller(
            database=database,
            user_interface=FakeUserInput(["1", "1", "3"]),
            external_dependency=external,
        )

        result = controller.run()
        record = database.get_record(1, 1, 3)

        self.assertIn("Тип: не треугольник", result)
        self.assertIsNotNone(record)
        self.assertEqual(record["triangle_type"], "не треугольник")
        self.assertEqual(len(external.sent_messages), 1)
        database.close()


if __name__ == "__main__":
    unittest.main()
