from django.shortcuts import render
from .models import *
from django.contrib.auth.decorators import login_required
@login_required
def index(request):
    """
    View function for home page of site
    """

    teams = Team.objects.all().order_by('team_code')
    # teams = reversed(teams)
    team_dictionary = {}

    for position, team in enumerate(teams):

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

        team_dictionary[team.team_code] = [position+1, team.image, team.current_price, next_fixture_opponent, next_fixture_time, total_invested]
    return render(request,'index.html',context={'teams': team_dictionary})

# @login_required
# def base(request):
#
#     if request.user.is_authenticated:
#
#         team_code = team_code.upper()
#         team = Team.objects.filter(team_code=team_code).get()
#         user = request.user
#         profile = Profile.objects.filter(user=user).get()
#         profile_cash = profile.cash_avaliable
#         if profile_cash == None:
#             profile_cash = '0'
#         investments=profile.total_invested
#
#         return render(request,'team.html',context={'cash':profile_cash,'investments':investments})

@login_required
def team(request, team_code):

        team_code = team_code.upper()
        team = Team.objects.filter(team_code=team_code).get()

        return render(request,'team.html',context={'team':team.team_code})
