from django.forms import ModelForm

from .models import AccountType, Account, Transaction

class AccountTypeForm(ModelForm):
    class Meta:
        model = AccountType
        fields = ['name', 'sign']

class AccountForm(ModelForm):
    pass

class TransactionForm(ModelForm):
    pass
