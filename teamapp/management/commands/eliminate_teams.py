import teamapp
import datetime
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):

    def handle(self, *args, **options):

        teams_to_go_out = ['KSA','EGY','MAR','IRN','AUS','PER','NGA','ISL','CRC',
                           'SRB','KOR','GER','PAN','TUN','POL','SEN']

        for team in teams_to_go_out:

            team_obj = teamapp.models.Team.objects.get(team_code = team)

            team_obj.eliminated = True

            team_obj.save() 
