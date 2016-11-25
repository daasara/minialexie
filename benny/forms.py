from django.forms import ModelForm

from .models import AccountType, Account, Transaction

class AccountTypeForm(ModelForm):
    class Meta:
        model = AccountType
        fields = ['name', 'sign']

class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ['accountType', 'name', 'budget']

class TransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ['description', 'amount', 'debit', 'credit', 'date']
