import teamapp

import datetime

all_users = teamapp.models.Profile.objects.all()

for user in all_users:

    teamapp.models.HistoricalInvestment.objects.create(user=user, total_value_of_investments=user.total_invested, total_cash_avaliable=user.cash_avaliable)
