from django.contrib import admin

from .models import Investment, Fixture, Team, ClosingValue

admin.site.register(Investment)
admin.site.register(Fixture)
admin.site.register(Team)
admin.site.register(ClosingValue)
