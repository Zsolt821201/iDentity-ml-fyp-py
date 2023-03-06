
# Use cases

## Change password

### Brief Description

    The user wants to change his password.

### Trigger Event

    The user clicks on the change password button.

### Main success Scenario

    The user enters his old password and his new password. 
    The user re-enters his new password. 
    The system will update the user password.

### Alternative Flows

    The user enters a wrong old password.The system will display an error message.
    The user enters a similar new password as the old password. The system will display an error message.
    the new password is not strong enough. The system will display an error message.
    the new password is not the same as the re-entered password. The system will display an error message.
    the new password less than 8 characters. The system will display an error message.

### Pre-Conditions

    The user is logged in.

### Post-Conditions

    The user password is updated.
