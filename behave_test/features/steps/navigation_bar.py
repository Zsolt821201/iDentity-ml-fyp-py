from behave import *

from behave_test.pom.location.Location import Location
from behave_test.pom.login.Login import Login

use_step_matcher("re")


@step("page is redirected into (.*) page")
def redirected_into_site(context, where):
    context.location = Location(context.driver)
    app_data = context.location.verify_redirection()
    assert app_data == where


@step("presented in (.*) site")
def step_impl(context, location):
    context.login = Login(context.driver)
    context.login.login_process(context.superuser_username,
                                context.superuser_password)
    redirected_into_site(context, location)


@then("applications headers are presented")
def step_impl(context):
    context.location = Location(context.driver)
    cleaned_data = []
    app_data = context.location.get_headers_links()
    # App data cleaner. Removing HTML pointer
    for x in app_data:
        cleaned_data.append(x.replace('\n(current)', ''))
    for row in context.table:
        assert row[0] in cleaned_data


@then("locations with email (.*) presented")
def step_impl(context, locations):
    context.location = Location(context.driver)
    locations = locations.split(',')
    for i in range(len(locations)):
        app_data = context.location.search_specific_location(locations[i])
        assert app_data, (print(f'{locations} is not presented in locations'))


@when("redirecting to (.*) sign in site")
def step_impl(context, location):
    context.location = Location(context.driver)
    context.location.click_activate_sign_in_btn(location)


@when("redirecting to (.*) sign out site")
def step_impl(context, location):
    context.location = Location(context.driver)
    context.location.click_activate_sign_out_btn(location)


@then("(.*) site presented")
def step_impl(context, label):
    context.location = Location(context.driver)
    app_data = context.location.label_content()
    assert app_data == label, (
        f'{app_data} is not {label} in {label} site presented step definition')
