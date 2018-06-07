from django.db import models
from django.db.models import Q
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save, post_init
from django.dispatch import receiver
from django.core.validators import MinValueValidator
from django.core.exceptions import ObjectDoesNotExist


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_invested = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    cash_avaliable = models.DecimalField(max_digits=5, decimal_places=2,
                                         null=True)
                                         # validators=[MinValueValidator('0.01')])

    def users_teams_investments(self):

        all_investments_by_user = Investment.objects.filter(user=self).values('id')
        all_teams_by_user = Investment.objects.filter(user=self).values('team_code')
        user_teams = {x['team_code']: 0 for x in all_teams_by_user}

        for investment in all_investments_by_user:
            user_teams[Investment.objects.get(id=investment['id']).team_code.team_code] += Investment.objects.get(id=investment['id']).number_shares * Investment.objects.get(id=investment['id']).transaction_type

        return user_teams

    def users_total_investments(user_teams):

        total_investment = 0

        for key, quant in user_teams.items():
            total_investment += Team.objects.get(team_code=key).current_price * quant

        return total_investment

    def __str__(self):

        return str(self.user)


class Team(models.Model):

    team_code = models.CharField(max_length=3, primary_key=True, help_text=
                                 "Team Code", verbose_name="Team Code")

    image = models.CharField(max_length=200, help_text="Location of flag image",
                             verbose_name="Image Location", blank=True)

    number_of_shares_held = models.IntegerField(help_text="Number of shares held",
                                                verbose_name="Number shares held")

    eliminated = models.BooleanField(default=False, help_text="Has team been \
                                     eliminated")

    current_price = models.IntegerField(help_text = "Current Price of the team",
                                        verbose_name = "Current Price")

    def total_shares_held(self):

        team = self.team_code

        all_investments_in_team = Investment.objects.filter(team_code=team).values('id')

        no_shares_held = 0

        for investment in all_investments_in_team:
            no_shares_held += Investment.objects.get(id=investment['id']).number_shares * Investment.objects.get(id=investment['id']).transaction_type

        return no_shares_held

    def total_invested_in_team(self):

        total_invested = self.current_price * self.number_of_shares_held

        return total_invested

    def is_trading_open(self):
#might not work
        try:
            time_of_cut_off = self.next_fixture()['date_time_fixture'] - datetime.timedelta(minutes=15)
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
                next_match = Fixture.objects.filter(Q(team_1=self.team_code) | Q(team_2=self.team_code)).filter(winner = None).order_by('date_time_fixture').values()[0]
                return next_match
            except IndexError:
                return "N/A"

    # def next_fixture_and_opponent(self):
    #
    #     next_fixture_var = self.next_fixture()
    #
    #     return next_fixture_var
    #
    #     # team = self.team_code
    #     #
    #     # if next_fixture_var.team_1 == team:
    #     #     return next_fixture_var.date_time_fixture, next_fixture_var.team_2
    #     # else:
    #     #     return next_fixture_var.date_time_fixture, next_fixture_var.team_1

    def __str__(self):

        return self.team_code

class HistoricalInvestments(models.Model):

    # Need to use celery to set this up

    """Model represeting historical size of investments by users"""

    user = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)

    datetime = models.DateTimeField(auto_now=True, help_text="Date and \
                                            Time of transaction",
                                            verbose_name="Transaction Date")

    total_value_of_investments = models.DecimalField(max_digits=5, decimal_places=2, null=True)

class Investment(models.Model):

    """Model representing each investment made by users"""

    user = models.ForeignKey(Profile, on_delete=models.DO_NOTHING)

    team_code = models.ForeignKey(Team,
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

    def collect_current_price(self):

        current_price = Team.objects.get(team_code=self.team_code).values('current_price')

    def generate_latest_price(x):
        team_data = Team.objects.get(team_code = x)
        return team_data.current_price

    def change_cash_avaliable(self):

        cash = Profile.objects.get(user=self.user).values('cash_avaliable')

        investment = self.transaction_type * self.price * self.number_shares

        user = Profile.objects.get(user=self.User)

        user.cash_avaliable= cash + investment
        user.save()

    def is_new_investment_ok(user, number_shares, team_code):

        cash = user.cash_avaliable
        team_price = Investment.generate_latest_price(team_code)
        cash_required = team_price * number_shares

        if cash_required > cash:
            return False
        else:
            return True

    def make_new_investment(user, team_code, number_shares, transaction_type):

        user = Profile.objects.get(user=user)
        team_code = Team.objects.get(team_code=team_code)
        price = team_code.current_price

        if Team.is_trading_open(team_code):
            if transaction_type == -1:
                new_investment = Investment.objects.create(user=user, team_code=team_code,
                                          number_shares=number_shares,
                                          transaction_type=transaction_type,
                                          transaction_mode=-1,
                                          price=price
                                          )

                new_investment.save()

            elif transaction_type == 1 and Investment.is_new_investment_ok(user, number_shares, team_code.team_code):
                new_investment = Investment.objects.create(user=user, team_code=team_code,
                                          number_shares=number_shares,
                                          transaction_type=transaction_type,
                                          transaction_mode=-1,
                                          price=price
                                          )

                new_investment.save()
        else:
            return "Trading is closed"

        # if transaction_type == -1 and Team.is_trading_open(team_code):

    # def post_new_investment


    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.).
        """

        if self.transaction_type > 0:
            transaction_type = 'Buy'
        else:
            transaction_type = 'Sell'
        return self.transaction_date.strftime('%d/%m/%Y %H:%M') + "--" + str(self.user) + "--" + str(self.price) + "--" + transaction_type

class Fixture(models.Model):

    """Model representing all of the fixtures in the tournament"""

    team_1 = models.ForeignKey(Team,
                               related_name="%(class)s_team1",
                               on_delete=models.DO_NOTHING)

    team_2 = models.ForeignKey(Team,
                               related_name="%(class)s_team2",
                               on_delete=models.DO_NOTHING)

    date_time_fixture = models.DateTimeField(help_text="Date and Time for fixture",
                                             verbose_name="Date and Time")

    round = models.CharField(max_length = 2, choices=(("gp","Group Stage"),("ko", "Knock Out")))

    team_1_goals = models.IntegerField(help_text="Number of goals Team 1 scored",
                                       verbose_name="Team 1 goals", null=True, blank=True)

    team_2_goals = models.IntegerField(help_text="Number of goals Team 2 scored",
                                       verbose_name="Team 2 goals", null=True, blank=True)

    team_choices = tuple((x['team_code'], x['team_code']) for x in Team.objects.all().values('team_code'))

    team_choices += (('draw', 'Draw'),(None, 'Null'))

    winner = models.CharField(max_length = 4, null=True, blank=True, choices=(team_choices))

    def __str__(self):

        return self.date_time_fixture.strftime('%d/%m/%Y - %H:%M') + ' - ' + str(self.team_1) + ' vs ' + str(self.team_2)

    # def __init__(self, *args, **kwargs):
    #     super(Fixture, self).__init__(*args, **kwargs)
    #     self.__original_winner = self.winner

    def is_winner_valid(self):

        if str(self.winner) not in [self.team_1.team_code, self.team_2.team_code, 'draw', None]:
            raise ValueError("Team is not in fixture so cannot win")

    def recalculate_share_prices_win(self):

        if self.round == 'gp':
            percentage = 0.5
        else:
            percentage = 1

        if self.team_1.team_code == str(self.winner):
            loser = self.team_2
        else:
            loser = self.team_1

        if Team.total_invested_in_team(loser) == 0:
            return "N/A"

        loser_value = Team.total_invested_in_team(loser) * percentage

        winner_no_shares = Team.objects.get(team_code=self.winner).number_of_shares_held
        loser_no_shares = Team.objects.get(team_code=loser.team_code).number_of_shares_held

        winner_share_price = Team.objects.get(team_code=self.winner).current_price
        loser_share_price = Team.objects.get(team_code=loser.team_code).current_price

        winner_new_share_price = loser_value/winner_no_shares + winner_share_price
        if percentage == 1:
            loser_new_share_price = 0
        else:
            loser_new_share_price = loser_value/loser_no_shares

        return {self.winner:winner_new_share_price, loser.team_code:loser_new_share_price}

    def update_share_prices(new_share_prices):

        if new_share_prices == "N/A":
            raise ValueError("No money invested in one team")
        else:
            for key, value in new_share_prices.items():
                 team = Team.objects.get(team_code=key)
                 team.current_price = value
                 team.save()


    def recalculate_share_prices_draw(self):

        team_1_value = Team.total_invested_in_team(self.team_1)
        team_2_value = Team.total_invested_in_team(self.team_2)

        if team_1_value == 0 or team_2_value == 0:
            return "N/A"
        else:
            difference = abs(team_1_value - team_2_value)/2

            if team_1_value >= team_2_value:

                team_1_value = team_1_value - difference
                team_2_value = team_2_value + difference

                team_1_shares = Team.objects.get(team_code=self.team_1).number_of_shares_held
                team_2_shares = Team.objects.get(team_code=self.team_2).number_of_shares_held

                team_1_new_share_price = team_1_value/team_1_shares
                team_2_new_share_price = team_2_value/team_2_shares

                return {self.team_1: team_1_new_share_price, self.team_2: team_2_new_share_price}

            elif team_2_value > team_1_value:

                team_1_value = team_1_value + difference
                team_2_value = team_2_value - difference

                team_1_shares = Team.objects.get(team_code=self.team_1).number_of_shares_held
                team_2_shares = Team.objects.get(team_code=self.team_2).number_of_shares_held

                team_1_new_share_price = team_1_value/team_1_shares
                team_2_new_share_price = team_2_value/team_2_shares

                return {self.team_1: team_1_new_share_price, self.team_2: team_2_new_share_price}


class ClosingValue(models.Model):

    team_code = models.ForeignKey(Team, on_delete=models.DO_NOTHING)

    date_time = models.DateTimeField(auto_now=True, help_text="Date and \
                                            Time of price",
                                     verbose_name="Closing Price Date")

    price = models.IntegerField(help_text="Price",
                                        verbose_name="Price")

    def deposit_closing_value(self):
        latest_price = Investment.generate_latest_price(self.team_code)
        ClosingValue.objects.create(team_code=self, price=latest_price)


    def __str__(self):

        return self.date_time.strftime('%d/%m/%Y') + ' - ' + str(self.team_code)+ ' - ' + str(self.price)

@receiver(post_save, sender=Investment)
def update_total_no_shares(sender, instance, created, **kwargs):
    team = Team.objects.get(team_code=instance.team_code)
    new_shares = Team.total_shares_held(instance.team_code)
    team.number_of_shares_held = new_shares
    team.save()

@receiver(pre_save, sender=Fixture)
def init_winner(sender, instance, **kwargs):
    if Fixture.objects.get(id=instance.id).winner == None and instance.winner == 'draw':
        new_prices = Fixture.recalculate_share_prices_draw(instance)
        Fixture.update_share_prices(new_prices)
    elif Fixture.objects.get(id=instance.id).winner == None and instance.winner != None:
        new_prices = Fixture.recalculate_share_prices_win(instance)
        Fixture.update_share_prices(new_prices)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

def __str__(self):
    return str(self.user)

# @receiver(post_save, sender=Fixture)
# def update_share_prices(sender, instance, created, raw, using, update_fields, **kwargs):
#     # print(init_winner(sender, instance, **kwargs))
#     if not created:
#         print(instance.winner)
#         print(instance.__original_winner)
#         # if instance.winner is not None or not "draw":
            # new_prices = Fixture.recalculate_share_prices_win(instance)
            # for key, value in new_prices.items():
            #     team = Team.objects.get(team_code=key)
            #     team.current_price = value
            #     team.save()
#         # else:
#         #     print("Hello")
