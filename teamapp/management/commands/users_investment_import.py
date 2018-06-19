import teamapp
import datetime
from django.core.management.base import BaseCommand, CommandError
from teamapp.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):

        all_users = Profile.objects.all()

        for user in all_users:

            HistoricalInvestment.objects.create(user=user, total_value_of_investments=user.total_invested, total_cash_avaliable=user.cash_avaliable)

            # self.stdout.write(self.style.SUCCESS('Successfully added user "%s"' % user))
