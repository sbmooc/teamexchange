from .models import *

def header_data(request):

    if request.user.is_authenticated:

        user = request.user
        profile = Profile.objects.filter(user=user).get()
        profile_cash = profile.cash_avaliable
        if profile_cash == None:
            profile_cash = '0'

        investments=profile.total_invested
        if investments == None:
            investments = '0'

    return {'wallet': profile_cash, 'investments': investments}
