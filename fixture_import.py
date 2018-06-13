import csv
import teamapp
from dateutil import parser


with open('fixtures.csv','rt') as csvfile:

    all_fixtures = csv.reader(csvfile, delimiter=',', quotechar='|')

    for row in all_fixtures:

        team_1 = teamapp.models.Team.objects.get(team_code=row[3])
        team_2 = teamapp.models.Team.objects.get(team_code=row[4])
        teamapp.models.Fixture.objects.create(team_1=team_1,team_2=team_2,date_time_fixture=parser.parse(row[2]),round=row[1],winner=None)
