import teamapp
import datetime
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):

    def handle(self, *args, **options):

        users = User.objects.all()

        for user in users:

            user_profile = teamapp.models.Profile.objects.get(user=user)

            for key, value in user_profile.users_teams_investments().items():

                if value > 0:

                    team = teamapp.models.Team.objects.get(team_code=key)

                    if team.eliminated:

                        current_price = team.current_price

                        teamapp.models.Investment.objects.create(user=user_profile,
                                                         team_code=team,
                                                         transaction_type = -1,
                                                         number_shares = value,
                                                         price = current_price,
                                                         transaction_mode = 1)

                        money_to_add_to_users_wallet = current_price * value

                        user_profile.cash_avaliable += money_to_add_to_users_wallet

                        user_profile.save()


                        print(user, team, user_profile.cash_avaliable)


                # print(team)
