# Generated by Django 2.0.5 on 2018-06-17 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teamapp', '0008_auto_20180617_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fixture',
            name='winner',
            field=models.CharField(blank=True, choices=[('SWE', 'SWE'), ('KOR', 'KOR'), ('SRB', 'SRB'), ('ARG', 'ARG'), ('ISL', 'ISL'), ('KSA', 'KSA'), ('COL', 'COL'), ('MEX', 'MEX'), ('NGA', 'NGA'), ('URU', 'URU'), ('CRO', 'CRO'), ('PAN', 'PAN'), ('BRA', 'BRA'), ('MAR', 'MAR'), ('RUS', 'RUS'), ('CRC', 'CRC'), ('GER', 'GER'), ('SUI', 'SUI'), ('BEL', 'BEL'), ('AUS', 'AUS'), ('EGY', 'EGY'), ('SEN', 'SEN'), ('TUN', 'TUN'), ('JPN', 'JPN'), ('PER', 'PER'), ('ESP', 'ESP'), ('ENG', 'ENG'), ('POR', 'POR'), ('IRN', 'IRN'), ('POL', 'POL'), ('DEN', 'DEN'), ('FRA', 'FRA'), ('draw', 'Draw'), (None, 'Null')], max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='historicalinvestment',
            name='datetime',
            field=models.DateField(auto_now=True, help_text='Date and                                             Time of transaction', verbose_name='Transaction Date'),
        ),
    ]
