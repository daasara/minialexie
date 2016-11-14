from django.http import HttpResponse
from django.shortcuts import render

from .models import AccountType, Account, Transaction
from .util import parse_from_date, parse_to_date
    
def index(request):
    from_date = parse_from_date(request)
    to_date = parse_to_date(request)
    
    account_types = AccountType.objects.filter(user=request.user)
    account_type_names = {}
    
    accounts = {}
    account_names = {}
    account_balances = {}
    
    for account_type in account_types:
        account_type_names[account_type.id] = account_type.name
        accounts[account_type.id] = Account.objects.filter(account_type=account_type.id)
        for account in accounts[account_type.id]:
            account_names[account.id] = account.name
            account_balances[account.id] = account.balance(from_date, to_date)
        
    return render(request, "alexie/index.html",
                  { 'account_type_names': account_type_names,
                    'accounts': accounts,
                    'account_names': account_names,
                    'account_balances': account_balances })
