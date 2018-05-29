# Generated by Django 2.0.5 on 2018-05-25 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Investments',
            fields=[
                ('investmentID', models.IntegerField(primary_key=True, serialize=False)),
                ('number_shares', models.IntegerField(help_text='Number of shares bought or                                         sold in this transaction', verbose_name='Number of Shares')),
                ('transaction_date', models.DateTimeField(auto_now=True, help_text='Date and                                             Time of transaction', verbose_name='Transaction Date')),
                ('transaction_type', models.IntegerField(choices=[(-1, 'Sell'), (1, 'Buy')], help_text='Show whether transaction                                           was a buy or sell', verbose_name='Transaction Type')),
                ('transaction_mode', models.IntegerField(choices=[(-1, 'User Generated'), (1, 'Automatically Generated')])),
            ],
        ),
    ]
