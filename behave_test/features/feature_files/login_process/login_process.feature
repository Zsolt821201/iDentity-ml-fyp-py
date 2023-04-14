# Created by zsolt.toth at 26/03/2023
@zsolt
Feature: Navigation bar test coverage

  @login
  Scenario: Navigation bar contains home link
    Given application is opened
    When successfully logged into system
    Then page is redirected into Locations page


  @login
  Scenario: Navigation bar contains home link - intended to fail
    Given application is opened
    When successfully logged into system
    Then page is redirected into Doesnt exist page

  @login
  Scenario: Unauthorized user cannot access application
    Given application is opened
    When unauthorized user is login into system
    Then login process denied

  @login
  Scenario: Login process failures without inserting credentials
    Given application is opened
    When clicking Login button without user credentials
    Then login process denied