from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('team/<str:team_code>', views.team, name='team-detail'),
    path('profile',views.profile,name='profile'),
    path('leaderboard',views.leaderboard,name='leaderboard'),
    path('faq',views.faq,name='faq'),
    path('game_rules',views.game_rules,name='rules')
]
