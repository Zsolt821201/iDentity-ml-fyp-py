import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Base:
    WEB_DRIVER_WAIT = 30

    def __init__(self, driver):
        self.driver = driver

    def type(self, locator, value):
        self.driver.find_element(By.CSS_SELECTOR, locator).send_keys(value)

    def type_text_to_element(self, text, element):
        time.sleep(0.3)
        self.clear(element)
        for char in text:
            time.sleep(0.05)
            self.type(element, char)

    def clear(self, locator):
        self.driver.find_element(By.CSS_SELECTOR, locator).clear()

    def return_locations(self, locator):
        return self.driver.find_elements(By.CSS_SELECTOR, locator)

    def visibility_of_element_presented(self, locator):
        WebDriverWait(self.driver, self.WEB_DRIVER_WAIT).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, locator)))

    def wait_till_element_clickable(self, locator):
        WebDriverWait(self.driver, self.WEB_DRIVER_WAIT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, locator)))

    def return_element_value(self, locator):
        self.visibility_of_element_presented(locator)
        element = self.driver.find_element(By.CSS_SELECTOR, locator)
        return element.text

    def get_element_attribute(self, locator, value):
        return self.driver.find_element(By.CSS_SELECTOR,
                                        locator).get_attribute(value)

    def click_element(self, locator):
        self.wait_till_element_clickable(locator)
        try:
            self.driver.find_element(By.CSS_SELECTOR, locator).click()
        except Exception as e:
            print(e)
