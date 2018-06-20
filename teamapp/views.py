from django.shortcuts import render
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import BuySell
from django.shortcuts import get_object_or_404
from django.contrib import messages
from decimal import *
import json

def share_price_change(team):

    last_two_values = ClosingValue.objects.filter(team_code=team).order_by('-date_time')

    if len(last_two_values) == 1:

        percentage_change = 0

    else:

        percentage_change = (last_two_values[0].new_price - last_two_values[1].new_price)/(last_two_values[1].new_price)

    return round(percentage_change,2) * 100

def user_value_change(user):

    user = Profile.objects.get(user=user)

    try:
        last_value = HistoricalInvestment.objects.filter(user=user).order_by('-datetime')[0]
        last_total = last_value.total_value_of_investments + last_value.total_cash_avaliable

    except IndexError:
        last_total = 20
    # print(last_value)

    current_investments_value = user.total_invested

    current_cash = user.cash_avaliable

    # print(last_total)
    current_total = current_cash + current_investments_value
    # print(current_total)

    percentage_change = (current_total - last_total)/last_total

    return round(percentage_change,2) * 100

def percentage_change_string(percentage):

    if percentage > 0:

        return "<span class='green'>" + str(percentage)+ "% </span>"

    elif percentage == 0:
        return str(percentage) + "%"

    else:

        return "<span class='red'>" + str(percentage)+ "% </span>"


@login_required
def index(request):
    """
    View function for home page of site
    """

    teams = Team.objects.all().order_by('team_code')

    team_dictionary = {}

    for team in teams:

        if team.is_trading_open():
            total_invested = round(team.current_price * team.number_of_shares_held,2)
        else:
            total_invested = "Trading open"

        percentage_change = percentage_change_string(share_price_change(team))

        team_dictionary[team.team_code] = [team.image, round(team.current_price,3), percentage_change]



    return render(request,'index.html',context={'teams': team_dictionary})


@login_required
def team(request, team_code):

        team_code = team_code.upper()
        team_code = get_object_or_404(Team, team_code = team_code)

        user = request.user

        team = Team.objects.filter(team_code=team_code).get()

        next_fixture = team.next_fixture()

        if next_fixture == 'N/A':
           next_fixture_opponent = 'N/A'
           next_fixture_time = ''
        else:
            if team.team_code == next_fixture['team_1_id']:
                next_fixture_opponent = next_fixture['team_2_id']
            else:
                next_fixture_opponent = next_fixture['team_1_id']

        next_fixture_time = next_fixture['date_time_fixture'] + datetime.timedelta(hours=1)
        next_fixture_time = next_fixture_time.strftime('%d/%m %H:%M')


        user_profile = Profile.objects.get(user=user)
        try:
            number_of_shares_held_in_team = user_profile.users_teams_investments()[str(team_code)]
        except KeyError:
            number_of_shares_held_in_team = 0

        total_value = team.number_of_shares_held * team.current_price

        is_trading_open = team.is_trading_open()

        closing_values = ClosingValue.objects.all().filter(team_code=team)

        # closing_value_list = []
        #
        # for value in closing_values:
        #
        #     year = value.date_time.year
        #     month = value.date_time.month -1
        #     day = value.date_time.day
        #
        #     closing_value_list = []
        #
        #     investment_list.extend((year,month,day,float(round(investment.total_value_of_investments,2)),float(round(investment.total_cash_avaliable,2))))
        #
        #     historical_investment_list.append(investment_list)



        if request.method=='POST':

            form = BuySell(request.POST, user=user, team_code=team_code)

            if form.is_valid():
                number_shares = form.cleaned_data.get('number_of_shares')
                transaction_type = form.cleaned_data.get('transaction_type')
                Investment.make_new_investment(user, team_code, number_shares, transaction_type)
                new_shares = int(number_shares) * int(transaction_type) + number_of_shares_held_in_team
                transaction_success = ""
                messages.success(request, 'Transaction successful')
                return render(request, 'team.html', context={'transaction_successful':transaction_success,'total_value':round(total_value,2),'trading_open':is_trading_open, 'team_code':team.team_code, 'flag': team.image, 'current_price': round(team.current_price,2), 'number_shares': new_shares, 'form':form, 'next_fixture_opp': next_fixture_opponent, 'next_fixture_time': next_fixture_time})

        else:
            form = BuySell()

        team_page = True

        percentage_change = share_price_change(team.team_code)

        if percentage_change >= 0:
            percentage_class = True
            percentage_change = '+' + str(percentage_change) + '%'
        else:
            percentage_class = False
            percentage_change = str(percentage_change) + '%'

        return render(request,'team.html',context={'total_value':round(total_value,2),'trading_open':is_trading_open, 'team_code':team.team_code, 'flag': team.image, 'current_price': round(team.current_price,3), 'number_shares': number_of_shares_held_in_team, 'form':form, 'team_page': team_page, 'percentage_change':percentage_change, 'next_fixture_opp': next_fixture_opponent, 'next_fixture_time': next_fixture_time, 'percentage_class': percentage_class})

@login_required
def profile(request):

    user = Profile.objects.get(user=request.user)

    user_teams = user.users_teams_investments()

    user_teams_dictionary = {}

    # print(user_teams.items())

    for team, shares in user_teams.items():

        team_flag = Team.objects.get(team_code=team).image

        team_price = Team.objects.get(team_code=team).current_price

        current_investment = team_price * shares

        if current_investment > 0:

            user_teams_dictionary[team] = [team_flag,shares,round(team_price,3), round(current_investment, 2)]

    historical_investments = HistoricalInvestment.objects.all().filter(user=user)

    historical_investment_list = []

    for investment in historical_investments:

        year = investment.datetime.year
        month = investment.datetime.month -1
        day = investment.datetime.day - 1

        investment_list = []

        investment_list.extend((year,month,day,float(round(investment.total_value_of_investments,2)),float(round(investment.total_cash_avaliable,2))))

        historical_investment_list.append(investment_list)


    if len(user_teams_dictionary) == 0:
        empty_profile = True
    else:
        empty_profile = False

    return render(request,'profile.html', context={'user_teams': user_teams_dictionary, 'empty_profile':empty_profile, 'chart_data':historical_investment_list})

@login_required
def leaderboard(request):

    ordered_users = Profile.objects.extra(
    select={'fieldsum':'total_invested + cash_avaliable'},
    order_by=('-fieldsum',))

    number_of_users = User.objects.all().filter(is_superuser=False).count()

    money_in_game = 20 * number_of_users

    leaderboard = {}

    for position, x in enumerate(ordered_users):

        if x.user.is_superuser:
            continue
        else:
            position = position
            id = x.id
            first_name = x.user.first_name
            last_name = x.user.last_name
            user_invested = x.total_invested
            user_cash = x.cash_avaliable
            if user_invested == None:
                user_invested = 0
            if user_cash == None:
                user_cash = 0
            total_money = user_invested + user_cash

            percentage_change = percentage_change_string(user_value_change(x.id))

            leaderboard[id]=[position+1, first_name, last_name, round(total_money,2), percentage_change]

    return render(request,'leaderboard.html',context={'users':leaderboard,'money_in_game':money_in_game,'number_of_users':number_of_users})

def fixtures(request):

    all_fixtures = Fixture.objects.all().order_by('date_time_fixture')

    today = datetime.datetime.now().date()
    fixtures_dictionary = {}

    # for fixture in all_fixtures:
    #     id = fixture.id
    #     if fixture.date_time_fixture.date() == today:
    #
    #         fixture_is_today = True
    #         fixtures_dictionary[id] =  {'fixture_is_today':fixture_is_today}
    #         break


    user = Profile.objects.get(user=request.user)

    counter = 1




    for fixture in all_fixtures:

        if fixture.date_time_fixture.date() == today and counter == 1 and fixture.winner == None:

            fixture_is_today = True

            counter += -1

        else:
            fixture_is_today = False


        id = fixture.id
        date_time = fixture.date_time_fixture + datetime.timedelta(hours=1)
        team_1 = Team.objects.get(team_code=fixture.team_1)
        team_2 = Team.objects.get(team_code=fixture.team_2)
        team_1_image = team_1.image
        team_2_image = team_2.image
        team_1 = fixture.team_1
        team_2 = fixture.team_2
        team_1_price = team_1.current_price
        team_2_price = team_2.current_price




        if fixture.winner != None:
            fixture_complete = True
            team_1_goals = fixture.team_1_goals
            team_2_goals = fixture.team_2_goals

        else:
            fixture_complete = False
            team_1_goals = None
            team_2_goals = None



        fixtures_dictionary[id] = {'date_time':date_time,
                                   'team_1': team_1,
                                   'team_2':team_2,
                                   'team_1_image':team_1_image,
                                   'team_2_image':team_2_image,
                                   'team_1_price':team_1_price,
                                    'team_2_price':team_2_price,
                                   'fixture_complete':fixture_complete,
                                    'team_1_goals':team_1_goals,
                                  'team_2_goals':team_2_goals,
                                  'fixture_is_today':fixture_is_today}

        if team_1.is_trading_open() is not True and team_2.is_trading_open() is not True:

            try:
                user_shares_team_1 = user.users_teams_investments()[team_1.team_code]
            except KeyError:
                user_shares_team_1 = 0

            try:
                user_shares_team_2 = user.users_teams_investments()[team_2.team_code]
            except KeyError:
                user_shares_team_2 = 0

            user_team_1_investment = user_shares_team_1 * team_1_price
            user_team_2_investment = user_shares_team_2 * team_2_price

            trading_is_closed = True

            team_1_shares = team_1.number_of_shares_held
            team_2_shares = team_2.number_of_shares_held


            team_1_total = team_1_shares * team_1_price
            team_2_total = team_2_shares * team_2_price

            round = fixture.round

            if round == 'gp':
                round_percentage = Decimal(0.5)
            else:
                round_percentage = Decimal(1)


            if team_1_total == 0 or team_2_total == 0:
                no_value_in_one_team = True

            else:
                team_1_win_change = ((((team_2_total * round_percentage) + team_1_total) - team_1_total) / team_1_total) * user_team_1_investment
                team_2_win_change = ((((team_1_total * round_percentage) + team_2_total) - team_2_total) / team_2_total) * user_team_2_investment


                new_value = (team_1_total + team_2_total)/ 2
                team_1_draw_change = ((new_value - team_1_total) / team_1_total) * user_team_1_investment
                team_2_draw_change = ((new_value - team_2_total) / team_2_total) * user_team_2_investment

                team_1_loss_change = (user_team_1_investment - ((round_percentage) * user_team_1_investment)) * -1
                team_2_loss_change = (user_team_2_investment - ((round_percentage) * user_team_2_investment)) * -1


                fixtures_dictionary[id].update({'team_1_win' : team_1_win_change,
                                           'team_2_win': team_2_win_change,
                                           'team_1_draw': team_1_draw_change,
                                           'team_2_draw': team_2_draw_change,
                                           'team_1_loss': team_1_loss_change,
                                           'team_2_loss': team_2_loss_change,
                                           'team_1_total':team_1_total,
                                           'team_2_total':team_2_total,
                                           'trading_is_closed' :trading_is_closed,
                                            'team_1_investment': user_team_1_investment,
                                            'team_2_investment': user_team_2_investment})

        else:

            trading_is_closed = False

            fixtures_dictionary[id].update({'trading_is_closed' :trading_is_closed })












        # print(fixtures_dictionary)



            # print(fixtures_dictionary)


    return render(request, 'fixtures.html', context={'fixtures_data': fixtures_dictionary})



def faq(request):

    return render(request,'faq.html')

def game_rules(request):

    return render(request,'game_rules.html')
