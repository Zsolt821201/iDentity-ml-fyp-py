# Created by zsolt.toth at 26/03/2023
Feature: Login process by using built-in user accounts

  @location
  Scenario: Application header contains all links
    Given application is opened
    When presented in Locations site
    Then applications headers are presented
      | Header Links             |
      | Home                     |
      | Locations                |
      | Edit Profile             |
      | Setup Facial Recognition |
      | Change Password          |
      | Logout                   |
      | Admin site               |

