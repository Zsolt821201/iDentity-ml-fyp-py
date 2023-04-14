import time
from behave_test.pom.Base import Base
from behave_test.pom.login.login_test import login, header


class Login(Base):
    def __init__(self, driver):
        super().__init__(driver)

    def trigger_login_page(self):
        locations = self.return_locations(header['header'])
        for i in range(len(locations)):
            if locations[i].text == 'Login':
                locations[i].click()

    def return_username_placeholder(self):
        return self.get_element_attribute(login['username'], 'placeholder')

    def login_process(self, username, password):
        self.visibility_of_element_presented(login['username'])
        for char in username:
            time.sleep(0.05)
            self.type(login['username'], char)

        for char in password:
            time.sleep(0.05)
            self.type(login['password'], char)

        self.clicking_login_button()

    def clicking_login_button(self):
        self.wait_till_element_clickable(login['login_btn'])
        self.click_element(login['login_btn'])
