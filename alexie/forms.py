from datetime import date

from django import forms

from .models import AccountType, Account

class AccountTypeForm(forms.ModelForm):
    class Meta:
        model = AccountType
        fields = ['id', 'name', 'sign']

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['id', 'account_type', 'name', 'budget']
        
class TransactionForm(forms.Form):
    # Verbose, first attempt. A ModelForm is more compact
    created = forms.DateField(initial=date.today)
    description = forms.CharField(max_length=200)
    amount = forms.CharField(max_length=32)
    # populate querysets in view because user is not known in advance
    debit = forms.ModelChoiceField(queryset=None)  
    credit = forms.ModelChoiceField(queryset=None)
