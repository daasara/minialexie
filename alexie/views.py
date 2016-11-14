from django.http import HttpResponse
from django.shortcuts import render

from .models import AccountType, Account, Transaction

def index(request):
    account_types = AccountType.objects.filter(user=request.user)

    account_type_names = {}
    accounts = {}
    for account_type in account_types:
        account_type_names[account_type.id] = account_type.name
        accounts[account_type.id] = Account.objects.filter(account_type=account_type.id)
        
    return render(request, "alexie/index.html",
                  { 'account_type_names': account_type_names,
                    'accounts': accounts })
