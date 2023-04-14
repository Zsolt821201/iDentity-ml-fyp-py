from selenium import webdriver
from behave_test.configuration_data import configuration_data


def before_all(context):
    configuration_data(context)


def before_scenario(context, driver):
    context.url = 'http://127.0.0.1:8000/'
    options = webdriver.ChromeOptions()
    context.driver = webdriver.Chrome(
        executable_path='behave_test/driver/chromedriver.exe', options=options)
    context.driver.implicitly_wait(50)
    context.driver.set_page_load_timeout(80)
