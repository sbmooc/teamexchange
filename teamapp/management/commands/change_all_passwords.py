import teamapp
import datetime
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):

    def handle(self, *args, **options):

        users = User.objects.all()

        for user in users:

            user.set_password('Hello1234')
            user.save()

            # self.stdout.write(self.style.SUCCESS('Successfully added user "%s"' % user))
