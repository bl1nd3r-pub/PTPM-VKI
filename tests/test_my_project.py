import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.my_project import (
    calculate_triangle_vertices,
    classify_triangle,
    parse_float_value,
    process_triangle_input,
)

ERROR_MARKER = [(-2, -2), (-2, -2), (-2, -2)]
NOT_TRIANGLE_MARKER = [(-1, -1), (-1, -1), (-1, -1)]


class TestParseFloatValue(unittest.TestCase):
    def test_parse_float_value_parses_plain_decimal(self):
        self.assertEqual(parse_float_value("3.5"), 3.5)

    def test_parse_float_value_parses_negative_number(self):
        self.assertEqual(parse_float_value("-2.25"), -2.25)

    def test_parse_float_value_ignores_surrounding_spaces(self):
        self.assertEqual(parse_float_value("   7.0   "), 7.0)
        self.assertEqual(parse_float_value("\t15.5\n"), 15.5)

    def test_parse_float_value_raises_on_non_numeric_text(self):
        with self.assertRaises(ValueError):
            parse_float_value("abc")
        with self.assertRaises(ValueError):
            parse_float_value("")

    def test_parse_float_value_raises_on_infinity(self):
        with self.assertRaises(ValueError):
            parse_float_value("inf")
        with self.assertRaises(ValueError):
            parse_float_value("1e400")

    def test_parse_float_value_raises_on_nan(self):
        with self.assertRaises(ValueError):
            parse_float_value("nan")


class TestClassifyTriangle(unittest.TestCase):
    def test_classify_triangle_returns_equilateral_for_three_equal_sides(self):
        self.assertEqual(classify_triangle(5, 5, 5), "равносторонний")

    def test_classify_triangle_returns_equilateral_for_equal_decimal_sides(self):
        self.assertEqual(classify_triangle(5.5, 5.5, 5.5), "равносторонний")

    def test_classify_triangle_accepts_sides_equal_within_float_tolerance(self):
        self.assertEqual(classify_triangle(0.1 + 0.2, 0.3, 0.3), "равносторонний")

    def test_classify_triangle_returns_isosceles_for_two_equal_sides(self):
        self.assertEqual(classify_triangle(6, 6, 8), "равнобедренный")

    def test_classify_triangle_returns_isosceles_for_nearly_equal_sides(self):
        self.assertEqual(classify_triangle(2.0, 2.0, 2.0 + 1e-6), "равнобедренный")

    def test_classify_triangle_returns_scalene_for_all_different_sides(self):
        self.assertEqual(classify_triangle(3, 4, 5), "разносторонний")

    def test_classify_triangle_returns_scalene_for_right_triangle(self):
        self.assertEqual(classify_triangle(7, 24, 25), "разносторонний")

    def test_classify_triangle_returns_not_triangle_for_zero_side(self):
        self.assertEqual(classify_triangle(0, 4, 5), "не треугольник")

    def test_classify_triangle_returns_not_triangle_for_negative_side(self):
        self.assertEqual(classify_triangle(-3, 4, 5), "не треугольник")

    def test_classify_triangle_returns_not_triangle_when_sum_equals_third_side(self):
        self.assertEqual(classify_triangle(5, 5, 10), "не треугольник")

    def test_classify_triangle_returns_not_triangle_when_sum_less_than_third_side(self):
        self.assertEqual(classify_triangle(1, 1, 5), "не треугольник")

    def test_classify_triangle_accepts_large_but_valid_sides(self):
        self.assertEqual(classify_triangle(100, 150, 200), "разносторонний")


class TestCalculateTriangleVertices(unittest.TestCase):
    def test_calculate_triangle_vertices_returns_three_points(self):
        vertices = calculate_triangle_vertices(3, 4, 5)
        self.assertEqual(len(vertices), 3)

    def test_calculate_triangle_vertices_returns_integer_coordinates(self):
        vertices = calculate_triangle_vertices(3, 4, 5)
        for x, y in vertices:
            self.assertIsInstance(x, int)
            self.assertIsInstance(y, int)

    def test_calculate_triangle_vertices_keeps_base_horizontal(self):
        vertices = calculate_triangle_vertices(3, 4, 5)
        self.assertEqual(vertices[0][1], vertices[1][1])

    def test_calculate_triangle_vertices_centers_apex_for_equilateral(self):
        vertices = calculate_triangle_vertices(5, 5, 5)
        self.assertEqual(vertices[2][0], 50)

    def test_calculate_triangle_vertices_clamps_points_to_canvas(self):
        vertices = calculate_triangle_vertices(3, 4, 5)
        for x, y in vertices:
            self.assertTrue(0 <= x <= 99)
            self.assertTrue(0 <= y <= 99)

    def test_calculate_triangle_vertices_handles_collinear_case_without_crash(self):
        vertices = calculate_triangle_vertices(1, 1, 2)
        self.assertEqual(len(vertices), 3)


class TestProcessTriangleInput(unittest.TestCase):
    def test_process_triangle_input_returns_scalene_for_valid_sides(self):
        triangle_type, vertices = process_triangle_input(["3", "4", "5"])
        self.assertEqual(triangle_type, "разносторонний")
        for x, y in vertices:
            self.assertTrue(0 <= x <= 99)

    def test_process_triangle_input_returns_equilateral_for_valid_sides(self):
        triangle_type, vertices = process_triangle_input(["7", "7", "7"])
        self.assertEqual(triangle_type, "равносторонний")

    def test_process_triangle_input_returns_error_marker_for_non_numeric(self):
        result = process_triangle_input(["a", "3", "4"])
        self.assertEqual(result, ("", ERROR_MARKER))

    def test_process_triangle_input_returns_error_marker_for_nan(self):
        result = process_triangle_input(["1", "nan", "2"])
        self.assertEqual(result, ("", ERROR_MARKER))

    def test_process_triangle_input_returns_error_marker_for_infinity(self):
        result = process_triangle_input(["1", "2", "1e400"])
        self.assertEqual(result, ("", ERROR_MARKER))

    def test_process_triangle_input_rejects_negative_side(self):
        result = process_triangle_input(["-3", "4", "5"])
        self.assertEqual(result, ("не треугольник", NOT_TRIANGLE_MARKER))

    def test_process_triangle_input_rejects_zero_side(self):
        result = process_triangle_input(["0", "4", "5"])
        self.assertEqual(result, ("не треугольник", NOT_TRIANGLE_MARKER))

    def test_process_triangle_input_rejects_impossible_side_lengths(self):
        result = process_triangle_input(["1", "1", "5"])
        self.assertEqual(result, ("не треугольник", NOT_TRIANGLE_MARKER))

    def test_process_triangle_input_rejects_too_few_values(self):
        result = process_triangle_input(["3", "4"])
        self.assertEqual(result, ("", ERROR_MARKER))

    def test_process_triangle_input_rejects_too_many_values(self):
        result = process_triangle_input(["3", "4", "5", "6"])
        self.assertEqual(result, ("", ERROR_MARKER))


if __name__ == "__main__":
    unittest.main()