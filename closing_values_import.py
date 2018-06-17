import teamapp
import datetime
from decimal import *

#So to create a datetime object, we pass in the year, month, day, hour, minute, and second.


all_teams = teamapp.models.Team.objects.all()

start_day_date_time = datetime.datetime(2018,6,14,12,0,0)

for team in all_teams:

    teamapp.models.ClosingValue.objects.create(team_code = team, new_price = 0.05, number_of_shares_held = None, date_time=start_day_date_time)

for team in all_teams:

    if team.current_price == Decimal('0.05'):
        continue
    else:
        teamapp.models.ClosingValue.objects.create(team_code = team, new_price = team.current_price, number_of_shares_held = team.number_of_shares_held)
