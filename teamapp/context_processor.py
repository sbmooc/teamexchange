from .models import *

def header_data(request):

    if request.user.is_authenticated:

        user = request.user
        profile = Profile.objects.filter(user=user).get()
        profile_cash = profile.cash_avaliable
        investments=profile.total_invested
        return {'wallet': profile_cash, 'investments': investments}
    else:
        return {'wallet': 0, 'investments':0}
