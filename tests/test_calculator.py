import unittest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

from pages.calculator_page import CalculatorPage


class CalculatorTests(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1280,720")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(30)
        for attempt in range(2):
            try:
                self.calculator = CalculatorPage(self.driver).open()
                break
            except TimeoutException:
                if attempt == 1:
                    raise
                self.driver.refresh()

    def tearDown(self):
        self.driver.quit()

    def assert_calculation(self, a, b, operation, expected):
        actual = self.calculator.calculate(a, b, operation)
        self.assertEqual(expected, actual)

    def test_addition(self):
        self.assert_calculation(7, 5, "+", "12")

    def test_subtraction(self):
        self.assert_calculation(7, 5, "-", "2")

    def test_multiplication(self):
        self.assert_calculation(7, 5, "*", "35")

    def test_division(self):
        self.assert_calculation(20, 4, "/", "5")

    def test_addition_with_negative_numbers(self):
        self.assert_calculation(-10, -5, "+", "-15")

    def test_subtraction_negative_result(self):
        self.assert_calculation(-3, 8, "-", "-11")

    def test_multiplication_by_zero(self):
        self.assert_calculation(123, 0, "*", "0")

    def test_decimal_calculation(self):
        self.assert_calculation(1.5, 2.25, "+", "3.75")

    def test_division_by_zero(self):
        actual = self.calculator.calculate(10, 0, "/")
        self.assertIn(actual, ("Infinity", "null"))

    def test_first_number_increment_and_decrement_buttons(self):
        self.calculator.enter_first_number(0)
        self.calculator.increment_first_number()
        self.assertEqual("1", self.calculator.get_result())
        self.calculator.decrement_first_number()
        self.assertEqual("0", self.calculator.get_result())

    def test_second_number_increment_and_decrement_buttons(self):
        self.calculator.enter_second_number(0)
        self.calculator.increment_second_number()
        self.assertEqual("1", self.calculator.get_result())
        self.calculator.decrement_second_number()
        self.assertEqual("0", self.calculator.get_result())


if __name__ == "__main__":
    unittest.main()
