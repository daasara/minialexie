from datetime import date

from django import forms

from .models import Account

class AccountTypeForm(forms.Form):
    name = forms.CharField(max_length=100)
    sign = forms.IntegerField()
    
class TransactionForm(forms.Form):
    created = forms.DateField(initial=date.today)
    description = forms.CharField(max_length=200)
    amount = forms.CharField(max_length=32)
    debit = forms.ModelChoiceField(queryset=None)  # populate in view
    credit = forms.ModelChoiceField(queryset=None)
    
