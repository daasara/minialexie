from math import ceil

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

    accountTypes = AccountType.objects.filter(user=request.user).order_by('order', 'name')

    for accountType in accountTypes:
        # call balance here, using the parsed from and to dates
        accountType.accountSummaries = []

        # sort by order field, using a temporary variable
        accountTypeAccounts = Account.objects.filter(user=request.user, account_type=accountType.id).order_by('order', 'name')
        
        for account in accountTypeAccounts:
            # fill in balances in order
            budget = account.budget
            datesBalance = account.balance(from_date, to_date)
            if budget > 0:
                percentSpent = str(ceil(datesBalance / budget * 100)) + "%"
            else:
                percentSpent = 0
                
            accountType.accountSummaries.append(
                { 'name': account.name,
                  'budget': budget, 
                  'datesBalance': datesBalance,
                  'percentSpent': percentSpent, })

    return render(request, 'benny/index.html',
                  { 'accountTypes': accountTypes })
