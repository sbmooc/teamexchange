# Generated by Django 2.0.5 on 2018-05-25 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teamapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fixtures',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_1', models.CharField(max_length=4)),
                ('team_2', models.CharField(max_length=4)),
                ('date_time_fixture', models.DateTimeField(help_text='Date and Time for fixture', verbose_name='Date and Time')),
                ('round', models.CharField(choices=[('gp', 'Group Stage'), ('ko', 'Knock Out')], max_length=2)),
                ('team_1_goals', models.IntegerField(help_text='Number of goals Team 1 scored', verbose_name='Team 1 goals')),
                ('team_2_goals', models.IntegerField(help_text='Number of goals Team 2 scored', verbose_name='Team 2 goals')),
                ('winner', models.CharField(choices=[(models.CharField(max_length=4), 'Team 1'), (models.CharField(max_length=4), 'Team 2'), ('draw', 'Draw')], max_length=4)),
            ],
        ),
    ]
