
# Roster

 A location sign-in/sign-out dates record of a user

## Active Sign In

 A Roster record with a sign-in date and no sign-out date.

# Day Roster

A collection of Roster records for a location with a sign-in dates for a given day.

Django Query

```py
location_day_roster_logs: list = Roster.objects.filter(
        location=location).values_list('sign_in_date__date', flat=True).distinct()
```

```py
roster_list = location.roster_set.filter(
        sign_in_date__date=location_sign_in_date)
```

