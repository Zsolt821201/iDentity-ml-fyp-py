from behave import *

from behave_test.pom.location.Location import Location

use_step_matcher("re")


@step("application is opened")
def step_impl(context):
    context.location = Location(context.driver)
    context.location.open_location(f'{context.url}locations')
