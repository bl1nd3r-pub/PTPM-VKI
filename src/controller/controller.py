import logging
from typing import Optional, Sequence, List

from src.calculation.triangle_validator import TriangleCalculator
from src.database.triangle_database import TriangleDatabase
from src.external_dependency.external_service import ExternalDependency
from src.user_interface.user_interface import UserInputInterface


class Controller:
    def __init__(
        self,
        calculator: Optional[TriangleCalculator] = None,
        database: Optional[TriangleDatabase] = None,
        user_interface: Optional[UserInputInterface] = None,
        external_dependency: Optional[ExternalDependency] = None,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.calculator = calculator or TriangleCalculator()
        self.database = database or TriangleDatabase()
        self.user_interface = user_interface
        self.external_dependency = external_dependency

    def _calculate_result(self, raw_values: Sequence[str]) -> str:
        triangle_type, vertices, error_message = self.calculator.calculate(raw_values)
        if triangle_type == "":
            return f"Ошибка: {error_message}"
        if triangle_type == "не треугольник":
            return f"Тип: {triangle_type}. {error_message}"
        return f"Тип: {triangle_type}. Вершины: {vertices}"

    def run(self) -> str:
        if self.user_interface is None:
            raise ValueError("Не задан интерфейс пользователя.")
        if self.external_dependency is None:
            raise ValueError("Не задана внешняя зависимость.")

        self.logger.info("Начало выполнения сценария контроллера")
        raw_values = self.user_interface.get_triangle_data()
        self.logger.info("Получены данные от пользователя: %s", raw_values)

        if len(raw_values) != 3:
            result = "Ошибка: Некорректное число входных значений."
            self.logger.warning("Некорректное число входных значений: %s", raw_values)
            self.external_dependency.send_result(result)
            return result

        try:
            values = [float(item) for item in raw_values]
        except ValueError:
            result = "Ошибка: Ввод содержит нечисловое значение."
            self.logger.error("Не удалось преобразовать входные значения к float: %s", raw_values)
            self.external_dependency.send_result(result)
            return result

        length1, length2, length3 = values
        cached = self.database.get_record(length1, length2, length3)
        if cached is not None:
            self.logger.info("Результат найден в БД: %s", cached)
            result = self._format_cached_result(cached)
            self.external_dependency.send_result(result)
            return result

        self.logger.info("В БД записи нет, вычисляем результат для сторон (%.2f, %.2f, %.2f)", length1, length2, length3)
        triangle_type, vertices, error_message = self.calculator.calculate(raw_values)
        if triangle_type == "":
            result = f"Ошибка: {error_message}"
            self.logger.error("Ошибка вычисления: %s", error_message)
            self.external_dependency.send_result(result)
            return result

        if triangle_type == "не треугольник":
            self.database.add_record(length1, length2, length3, triangle_type, error_message)
            result = f"Тип: {triangle_type}. {error_message}"
            self.logger.warning("Стороны не образуют треугольник: %s", result)
            self.external_dependency.send_result(result)
            return result

        self.database.add_record(length1, length2, length3, triangle_type, "")
        result = f"Тип: {triangle_type}. Вершины: {vertices}"
        self.logger.info("Результат вычислен и сохранён: %s", result)
        self.external_dependency.send_result(result)
        return result

    def _format_cached_result(self, cached: dict) -> str:
        if cached["error_message"]:
            return f"Тип: {cached['triangle_type']}. {cached['error_message']}"

        triangle_type, vertices, _ = self.calculator.calculate(
            [str(cached["length1"]), str(cached["length2"]), str(cached["length3"])]
        )
        return f"Тип: {triangle_type}. Вершины: {vertices}"
