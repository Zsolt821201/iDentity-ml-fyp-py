# Created by zsolt.toth at 07/04/2023
Feature: Sign in activation feature

  @locations
  Scenario: 2 default locations exist
    Given application is opened
    When presented in Locations site
    Then locations with email Limerick@identify.com,Cork@identify.com presented


  @locations
  Scenario: Redirection to Limerick sign in site
    Given application is opened
    When presented in Locations site
    And redirecting to Limerick@identify.com sign in site
    Then Limerick Sign In site presented


  @locations
  Scenario: Redirection to Cork sign in site
    Given application is opened
    When presented in Locations site
    And redirecting to Cork@identify.com sign in site
    Then Cork Sign In site presented


  @locations
  Scenario: Redirection to Limerick sign out site
    Given application is opened
    When presented in Locations site
    And redirecting to Limerick@identify.com sign out site
    Then Limerick Sign Out site presented