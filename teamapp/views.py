from django.shortcuts import render
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import BuySell
from django.shortcuts import get_object_or_404
from django.contrib import messages

def share_price_change(team):

    last_two_values = ClosingValue.objects.filter(team_code=team).order_by('-date_time')

    if len(last_two_values) == 1:

        percentage_change = 0

    else:

        percentage_change = (last_two_values[0].new_price - last_two_values[1].new_price)/(last_two_values[1].new_price)

    return round(percentage_change,2) * 100

def user_value_change(user):

    user = Profile.objects.get(user=user)

    last_value = HistoricalInvestment.objects.filter(user=user).order_by('-datetime')[0]
    print(last_value)

    current_investments_value = user.total_invested

    current_cash = user.cash_avaliable

    last_total = last_value.total_value_of_investments + last_value.total_cash_avaliable
    print(last_total)
    current_total = current_cash + current_investments_value
    print(current_total)

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

        next_fixture = team.next_fixture()
        if next_fixture == 'N/A':
           next_fixture_opponent = 'N/A'
           next_fixture_time = ''
        else:
            if team.team_code == next_fixture['team_1_id']:
                next_fixture_opponent = next_fixture['team_2_id']
                next_fixture_time = next_fixture['date_time_fixture'] + datetime.timedelta(hours=1)
                next_fixture_time = next_fixture_time.strftime('%d/%m %H:%M')
            else:
                next_fixture_opponent = next_fixture['team_1_id']
                next_fixture_time = next_fixture['date_time_fixture'] + datetime.timedelta(hours=1)
                next_fixture_time = next_fixture_time.strftime('%d/%m %H:%M')

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

        user_profile = Profile.objects.get(user=user)
        try:
            number_of_shares_held_in_team = user_profile.users_teams_investments()[str(team_code)]
        except KeyError:
            number_of_shares_held_in_team = 0

        total_value = team.number_of_shares_held * team.current_price

        is_trading_open = team.is_trading_open()

        if request.method=='POST':

            form = BuySell(request.POST, user=user, team_code=team_code)

            if form.is_valid():
                number_shares = form.cleaned_data.get('number_of_shares')
                transaction_type = form.cleaned_data.get('transaction_type')
                Investment.make_new_investment(user, team_code, number_shares, transaction_type)
                new_shares = int(number_shares) * int(transaction_type) + number_of_shares_held_in_team
                transaction_success = ""
                messages.success(request, 'Transaction successful')
                return render(request, 'team.html', context={'transaction_successful':transaction_success,'total_value':round(total_value,2),'trading_open':is_trading_open, 'team_code':team.team_code, 'flag': team.image, 'current_price': round(team.current_price,2), 'number_shares': new_shares, 'form':form})

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

        return render(request,'team.html',context={'total_value':round(total_value,2),'trading_open':is_trading_open, 'team_code':team.team_code, 'flag': team.image, 'current_price': round(team.current_price,3), 'number_shares': number_of_shares_held_in_team, 'form':form, 'team_page': team_page, 'percentage_change':percentage_change, 'percentage_class': percentage_class})

@login_required
def profile(request):

    user = Profile.objects.get(user=request.user)

    user_teams = user.users_teams_investments()

    user_teams_dictionary = {}

    print(user_teams.items())

    for team, shares in user_teams.items():

        team_flag = Team.objects.get(team_code=team).image

        team_price = Team.objects.get(team_code=team).current_price

        current_investment = team_price * shares

        if current_investment > 0:

            user_teams_dictionary[team] = [team_flag,shares,round(team_price,3), round(current_investment, 2)]


    if len(user_teams_dictionary) == 0:
        empty_profile = True
    else:
        empty_profile = False

    return render(request,'profile.html', context={'user_teams': user_teams_dictionary, 'empty_profile':empty_profile})

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

def faq(request):

    return render(request,'faq.html')

def game_rules(request):

    return render(request,'game_rules.html')
