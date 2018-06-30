import teamapp
import datetime
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):

    def handle(self, *args, **options):

        seventeen_aug = datetime.date(2018,7,17)

        all_fixtures = teamapp.models.Fixture.objects.all()

        for fixture in all_fixtures:

            if fixture.date_time_fixture.date() > seventeen_aug:

                fixture.delete()
