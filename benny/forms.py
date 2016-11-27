from django import forms

from .models import AccountType, Account, Transaction

class AccountTypeForm(forms.ModelForm):
    class Meta:
        model = AccountType
        fields = ['name', 'sign']

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['accountType', 'name', 'budget']

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['description', 'amount', 'debit', 'credit', 'date']
        widgets = {
            'description': forms.TextInput(attrs={'size': 60}),
        }
