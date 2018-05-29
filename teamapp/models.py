from django.db import models
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

    def nearest(items, pivot):
        return min(items, key=lambda x: abs(x - pivot))

    def next_fixture(self):
        match_1 = Fixture.objects.filter(team_1=self.team_code).order_by('date_time_fixture')
        match_2 = Fixture.objects.filter(team_1=self.team_code).order_by('date_time_fixture')

        return match_1

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

    winner = models.CharField(max_length = 4, null=True, blank=True, choices=((team_1, "Team 1"), (team_2, "Team 2"),
                                       ("draw", "Draw"),(None, "Null")))

    # planning to build a small function here that updates the currently in play
    # value to true if the date time of now is less than 15 mins from the fixture
    # then, will have in the Team class - look to see if there are any Fixture
    # for the team in which the currently in play is TRUE and winner is NULL
    # if so, then trading is suspended

    def is_fixture_in_play(date_time_fixture):
        in_play = False

        if datetime.now() > (date_time_fixture - datetime.timedelta(minutes = -15)):
            in_play = True

        return in_play

    def __str__(self):

        return str(self.date_time_fixture)


class ClosingValue(models.Model):

    team_code = models.ForeignKey('Team', on_delete=models.DO_NOTHING)

    date_time = models.DateTimeField(auto_now=True, help_text="Date and \
                                            Time of price",
                                     verbose_name="Closing Price Date")

    price = models.IntegerField(help_text="Price",
                                        verbose_name="Price")

    def __str__(self):

        return self.team_code, self.price
