# Generated by Django 2.0.5 on 2018-06-17 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teamapp', '0007_auto_20180617_1114'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='closingvalue',
            name='price',
        ),
        migrations.AddField(
            model_name='closingvalue',
            name='new_price',
            field=models.DecimalField(decimal_places=8, help_text='Current Price of the team', max_digits=50, null=True, verbose_name='Current Price'),
        ),
        migrations.AddField(
            model_name='closingvalue',
            name='number_of_shares_held',
            field=models.IntegerField(help_text='Number of shares held', null=True, verbose_name='Number shares held'),
        ),
    ]
