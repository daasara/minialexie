from django.shortcuts import render

from .models import AccountType, Account, Transaction
from .util import parse_from_date, parse_to_date

def index(request):
    """
    Display all account balances in the selected time period.
    """

    if not request.user.is_authenticated():
        return redirect('/auth/login/')

    from_date = parse_from_date(request)
    to_date = parse_to_date(request)

    accountTypes = AccountType.objects.filter(user=request.user).order_by('order')

    accountTypeBalances = {}

    for accountType in accountTypes:
        accountTypeBalances[accountType.id] = Account.objects.filter(user=request.user, account_type=accountType

    return render(request, 'benny/index.html',
                  { 'accountTypes': accountTypes })
                  
