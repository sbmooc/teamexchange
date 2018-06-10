from django.shortcuts import render
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import BuySell
from django.shortcuts import get_object_or_404

@login_required
def index(request):
    """
    View function for home page of site
    """

    teams = Team.objects.all().order_by('team_code')
    users_set = User.objects.all()
    # teams = reversed(teams)
    team_dictionary = {}

    for team in teams:

        next_fixture = team.next_fixture()
        if next_fixture == 'N/A':
           next_fixture_opponent = 'N/A'
           next_fixture_time = ''
        else:
            if team.team_code == next_fixture['team_1_id']:
                next_fixture_opponent = next_fixture['team_2_id']
                next_fixture_time = next_fixture['date_time_fixture'].strftime('%d/%m %H:%M')
            else:
                next_fixture_opponent = next_fixture['team_1_id']
                next_fixture_time = next_fixture['date_time_fixture'].strftime('%d/%m %H:%M')

        if team.is_trading_open():
            total_invested = team.current_price * team.number_of_shares_held
        else:
            total_invested = "Trading open"

        team_dictionary[team.team_code] = [team.image, team.current_price, next_fixture_opponent, next_fixture_time, total_invested]

    leaderboard = {}

    print(users_set)
    print(users_set[0].profile.total_invested)

    for position, x in enumerate(users_set):
        position = position
        id = x.id
        first_name = x.first_name
        last_name = x.last_name
        user_invested = x.profile.total_invested
        user_cash = x.profile.cash_avaliable
        if user_invested == None:
            user_invested = 0
        if user_cash == None:
            user_cash = 0
        total_money = user_invested + user_cash

        leaderboard[id]=[position+1, first_name, last_name, total_money]


    return render(request,'index.html',context={'teams': team_dictionary, 'users':leaderboard})


@login_required
def team(request, team_code):

        team_code = team_code.upper()
        team_code = get_object_or_404(Team, team_code = team_code)

        user = request.user


        team = Team.objects.filter(team_code=team_code).get()

        total_value = team.number_of_shares_held * team.current_price

        is_trading_open = team.is_trading_open()

        if request.method=='POST':

            form = BuySell(request.POST, user=user, team_code=team_code)

            if form.is_valid():
                number_shares = form.cleaned_data['number_of_shares']
                transaction_type = form.cleaned_data['transaction_type']
                Investment.make_new_investment(user, team_code, number_shares, transaction_type)

        else:
            form = BuySell()

        return render(request,'team.html',context={'total_value':total_value,'trading_open':is_trading_open, 'team_code':team.team_code, 'flag': team.image, 'current_price': team.current_price, 'form':form})
