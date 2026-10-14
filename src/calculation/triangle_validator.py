from typing import Sequence, Tuple, List

from .triangle_logic import classify_triangle, parse_float_value


class TriangleCalculator:
    """Wraps triangle validation logic from the Lab 1 implementation."""

    def calculate(self, raw_values: Sequence[str]) -> Tuple[str, List[Tuple[int, int]], str]:
        if len(raw_values) != 3:
            return "", [(-2, -2), (-2, -2), (-2, -2)], "Некорректное число входных значений."

        try:
            values = [parse_float_value(str(value)) for value in raw_values]
        except ValueError:
            return "", [(-2, -2), (-2, -2), (-2, -2)], "Ввод содержит нечисловое значение."

        a, b, c = values
        triangle_type = classify_triangle(a, b, c)
        if triangle_type == "не треугольник":
            return triangle_type, [(-1, -1), (-1, -1), (-1, -1)], "Треугольник не может быть построен по данным сторонам."

        from .triangle_logic import calculate_triangle_vertices

        vertices = calculate_triangle_vertices(a, b, c)
        return triangle_type, vertices, ""
