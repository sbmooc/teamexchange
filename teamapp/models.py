from django.db import models
from django.db.models import Q
import datetime



class Team(models.Model):

    team_code = models.CharField(max_length=3, primary_key=True, help_text=
                                 "Team Code", verbose_name="Team Code")

    image = models.CharField(max_length=100, help_text="Location of flag image",
                             verbose_name="Image Location", blank=True)

    number_of_shares_held = models.IntegerField(help_text="Number of shares held",
                                                verbose_name="Number shares held")

    eliminated = models.BooleanField(default=False, help_text="Has team been \
                                     eliminated")

    current_price = models.IntegerField(help_text = "Current Price of the team",
                                        verbose_name = "Current Price")

    def is_trading_open(self):
        try:
            time_of_cut_off = self.next_fixture() - datetime.timedelta(minutes=15)
            if datetime.datetime.now(datetime.timezone.utc) > time_of_cut_off:
                return False
            else:
                return True
        except TypeError:
            return False

    def next_fixture(self):
        if self.eliminated:
            return "N/A"
        else:
            try:
                next_match = Fixture.objects.filter(Q(team_1=self.team_code) | Q(team_2=self.team_code)).filter(winner = None).order_by('date_time_fixture').values('date_time_fixture')[0]['date_time_fixture']
                return next_match
            except IndexError:
                return "N/A"

    def __str__(self):

        return self.team_code


class Investment(models.Model):

    """Model representing each investment made by users"""

    # UserID

    def generate_latest_price(x):
        team_data = Team.objects.get(team_code = x)
        return team_data.current_price


    team_code = models.ForeignKey('Team',
                               on_delete=models.DO_NOTHING)

    transaction_type = models.IntegerField(choices=((-1, "Sell"), (1, "Buy")),
                                           help_text="Show whether transaction\
                                           was a buy or sell",
                                           verbose_name="Transaction Type")

    number_shares = models.IntegerField(help_text="Number of shares bought or \
                                        sold in this transaction",
                                        verbose_name="Number of Shares")

    price = models.IntegerField(help_text="")

    transaction_date = models.DateTimeField(auto_now=True, help_text="Date and \
                                            Time of transaction",
                                            verbose_name="Transaction Date")

    transaction_mode = models.IntegerField(choices=((-1, "User Generated"),
                                                    (1,
                                                     "Automatically Generated")))



    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.).
        """
        return self.investmentID

class Fixture(models.Model):

    """Model representing all of the fixtures in the tournament"""

    team_1 = models.ForeignKey('Team',
                               related_name="%(class)s_team1",
                               on_delete=models.DO_NOTHING)
    team_2 = models.ForeignKey('Team',
                               related_name="%(class)s_team2",
                               on_delete=models.DO_NOTHING)

    date_time_fixture = models.DateTimeField(help_text="Date and Time for fixture",
                                             verbose_name="Date and Time")

    round = models.CharField(max_length = 2, choices=(("gp","Group Stage"),("ko", "Knock Out")))

    team_1_goals = models.IntegerField(help_text="Number of goals Team 1 scored",
                                       verbose_name="Team 1 goals", null=True, blank=True)

    team_2_goals = models.IntegerField(help_text="Number of goals Team 2 scored",
                                       verbose_name="Team 2 goals", null=True, blank=True)

    winner = models.CharField(max_length = 4, null=True, blank=True, choices=(('1', "Team 1"), ('2', "Team 2"),
                                       ("draw", "Draw"),(None, "Null")))

    def __str__(self):

        return self.date_time_fixture.strftime('%d/%m/%Y - %H:%M') + ' - ' + str(self.team_1) + ' vs ' + str(self.team_2)


class ClosingValue(models.Model):

    team_code = models.ForeignKey('Team', on_delete=models.DO_NOTHING)

    date_time = models.DateTimeField(auto_now=True, help_text="Date and \
                                            Time of price",
                                     verbose_name="Closing Price Date")

    price = models.IntegerField(help_text="Price",
                                        verbose_name="Price")

    def deposit_current_price(self):
        latest_price = Investment.generate_latest_price(self.team_code)
        ClosingValue.objects.create(team_code=self.team_code, price=latest_price)



    def __str__(self):

        return self.date_time.strftime('%d/%m/%Y') + ' - ' + str(self.team_code)+ ' - ' + str(self.price)

current_team = Team.objects.get(team_code="POR")
