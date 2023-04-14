from behave_test.pom.Base import Base
from behave_test.pom.location.location_test import label, header, table, \
    row_positions


class Location(Base):
    def __init__(self, driver):
        super().__init__(driver)

    def open_location(self, url):
        self.driver.get(url)

    def verify_redirection(self):
        self.visibility_of_element_presented(label['location_label'])
        return self.return_element_value(label['location_label'])

    def get_headers_links(self):
        app_links = []
        data = self.return_locations(header['header_links'])
        for i in range(len(data)):
            app_links.append(data[i].text)
        return app_links

    def search_specific_location(self, location):
        rows = self.return_locations(table['content'])
        for i in range(len(rows)):
            source_value = row_positions(i + 1, 3)
            if self.return_element_value(source_value) == location:
                return True
        return False

    def click_activate_sign_in_btn(self, location):
        rows = self.return_locations(table['content'])
        for i in range(len(rows)):
            source_value = row_positions(i + 1, 3)
            if self.return_element_value(source_value) == location:
                self.click_element(row_positions(i + 1, 5))
                break

    def click_activate_sign_out_btn(self, location):
        rows = self.return_locations(table['content'])
        for i in range(len(rows)):
            source_value = row_positions(i + 1, 3)
            if self.return_element_value(source_value) == location:
                self.click_element(row_positions(i + 1, 6))
                break

    def label_content(self):
        return self.return_element_value(label['sign_in_label'])
