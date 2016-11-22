from datetime import date

from django import forms

from .models import Account

class TransactionForm(forms.Form):
    created = forms.DateField(initial=date.today)
    description = forms.CharField(max_length=200)

    # FIXME switch to CharField, manually parse input like 1,20 and 1.20
    # should accept both dots and commas 
    amount = forms.IntegerField()
    debit = forms.ModelChoiceField(queryset=None)  # populate in view
    credit = forms.ModelChoiceField(queryset=None)
    
