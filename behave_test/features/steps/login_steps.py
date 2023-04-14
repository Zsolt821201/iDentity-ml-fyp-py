from behave import *

from behave_test.pom.login.Login import Login


@step("successfully logged into system")
def step_impl(context):
    context.login = Login(context.driver)
    context.login.login_process(context.superuser_username,
                                context.superuser_password)


@step("unauthorized user is login into system")
def step_impl(context):
    context.login = Login(context.driver)
    context.login.login_process('I am username', 'I am password')


@step("clicking Login button without user credentials")
def step_impl(context):
    context.login = Login(context.driver)
    context.login.clicking_login_button()


@step("login process denied")
def step_impl(context):
    context.login = Login(context.driver)
    app_data = context.login.return_username_placeholder()
    assert app_data == 'Enter User Name'
