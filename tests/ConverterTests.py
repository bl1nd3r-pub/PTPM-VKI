import unittest
from src.Converter import Converter


class ConverterTests(unittest.TestCase):
    def test_do_greater_than_100_7(self):
        self.assertEqual(Converter.do(110.0), 1000)
    def test_do_boundary_100_7(self):
        self.assertEqual(Converter.do(100.7), 1000)
    def test_do_positive_range_100_7(self):
        x = 42.3
        self.assertEqual(Converter.do(x), int(x))
    def test_do_boundary_just_above_zero(self):
        self.assertEqual(Converter.do(0.1), 0)
    def test_do_zero_raises_value_error(self):
        with self.assertRaises(ValueError):
            Converter.do(0.0)
    def test_do_range_minus_30_4(self):
        x = -23.6
        self.assertEqual(Converter.do(x), int(x)-5)
    def test_do_boundary_minus_30_4(self):
        x = -30.4
        self.assertEqual(Converter.do(x), int(x)-5)
    def test_do_boundary_minus_30_5(self):
        x = -30.5
        self.assertEqual(Converter.do(x), -2000)
    def test_do_less_than_minus_30_5(self):
        x = -424.2
        self.assertEqual(Converter.do(x), -2000)

if __name__ == '__main__':
    unittest.main()
