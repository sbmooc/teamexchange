from django import forms
from django.core.exceptions import ValidationError
from .models import Profile, Investment

class BuySell(forms.Form):

    transaction_type = forms.ChoiceField(choices=((-1, "Sell"), (1, "Buy")))
    number_of_shares = forms.IntegerField(localize=True)

    # print(cleaned_data)

    # print(transaction_type)
    # print(number_of_shares)
    # choices=((-1, "Sell"), (1, "Buy"))

    def clean_transaction_type(self):

        transaction_type=self.cleaned_data['transaction_type']


        return transaction_type

    def clean_number_of_shares(self):


        number_shares = self.cleaned_data['number_of_shares']
        transaction_type = self.clean_transaction_type()

        if Investment.is_new_investment_ok(self.user, number_shares, self.team_code, transaction_type):
            return number_shares
        else:
            raise ValidationError('Sorry you can\'t do that')



    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user',None)
        self.team_code = kwargs.pop('team_code',None)
        super(BuySell, self).__init__(*args, **kwargs)

class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
