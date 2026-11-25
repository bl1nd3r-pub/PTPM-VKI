from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait


class CalculatorPage:
    URL = "https://www.globalsqa.com/angularJs-protractor/SimpleCalculator/"

    def __init__(self, driver):
        self._driver = driver
        self._first_number = (By.CSS_SELECTOR, "input[ng-model='a']")
        self._second_number = (By.CSS_SELECTOR, "input[ng-model='b']")
        self._operation = (By.CSS_SELECTOR, "select[ng-model='operation']")
        self._result = (By.CSS_SELECTOR, "b.result")

    def open(self):
        self._driver.get(self.URL)
        WebDriverWait(self._driver, 20).until(
            EC.presence_of_element_located(self._first_number)
        )
        return self

    def enter_first_number(self, number):
        field = WebDriverWait(self._driver, 10).until(
            EC.visibility_of_element_located(self._first_number)
        )
        field.clear()
        field.send_keys(str(number))

    def enter_second_number(self, number):
        field = WebDriverWait(self._driver, 10).until(
            EC.visibility_of_element_located(self._second_number)
        )
        field.clear()
        field.send_keys(str(number))

    def select_operation(self, operation):
        Select(self._driver.find_element(*self._operation)).select_by_value(operation)

    def increment_first_number(self):
        self._click_button("inca")

    def decrement_first_number(self):
        self._click_button("deca")

    def increment_second_number(self):
        self._click_button("incb")

    def decrement_second_number(self):
        self._click_button("decb")

    def get_result(self):
        result_text = WebDriverWait(self._driver, 10).until(
            lambda driver: driver.find_element(*self._result).text
        )
        if "=" not in result_text:
            return ""
        return result_text.rsplit("=", 1)[1].strip()

    def calculate(self, first_number, second_number, operation):
        self.enter_first_number(first_number)
        self.enter_second_number(second_number)
        self.select_operation(operation)
        return self.get_result()

    def _click_button(self, angular_action):
        button = self._driver.find_element(
            By.XPATH, f"//button[@ng-click='{angular_action}()']"
        )
        button.click()
