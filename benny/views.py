from math import ceil

from django.urls import reverse
from django.db.models import Max
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url

from .models import AccountType, Account, Transaction
from .forms import AccountTypeForm, AccountForm, TransactionForm
from .util import parse_from_date, parse_to_date

def summarizeAccounts(accounts, from_date, to_date):
    accountSummaries = []
    for account in accounts:
        budget = account.budget
        datesBalance = account.balance(from_date, to_date)
        if budget > 0:
            percentSpent = ceil(datesBalance / budget * 100)
        else:
            percentSpent = 0
        accountSummaries.append(
            { 'name': account.name,
              'budget': budget,
              'datesBalance': datesBalance,
              'percentSpent': percentSpent, })
    return accountSummaries

def parseAccountTypeSign(value):
    # Given a form's value, return +/-1
    if value == 0:
        return 1
    else:
        return round(value / abs(value))
    
def index(request):
    """
    Display all account balances in the selected time period.
    """
    if not request.user.is_authenticated():
        return redirect('/auth/login/')

    accountTypes = AccountType.objects.filter(user=request.user).order_by('order', 'name')

    for accountType in accountTypes:
        # use a temporary variable for current AccountType
        # sort by order field then by name
        accountTypeAccounts = Account.objects.filter(user=request.user, accountType=accountType.id).order_by('order', 'name')

        # retrieve balances here, using the parsed from and to dates
        accountType.accountSummaries = summarizeAccounts(accountTypeAccounts, parse_from_date(request), parse_to_date(request))

    return render(request, 'benny/index.html',
                  { 'accountTypes': accountTypes })

# For every model, there are up to eight functions
#
#               AccountType   Account    Transaction
#        create     done
#    saveCreate     done
#          read     done
#        update     done
#    saveUpdate     done
# confirmDelete     done
#        delete     done
#    bulkDelete    ( not available )    via checkboxes

###############
# AccountType #
###############

def accountTypeCreate(request):
    form = AccountTypeForm()
    return render(request, 'benny/accountTypeCreate.html',
                  { 'form': form })

def accountTypeSaveCreate(request):
    if request.method == "POST":
        form = AccountTypeForm(request.POST)
        if form.is_valid():
            accountType = AccountType()
            accountType.user = request.user
            accountType.name = form.cleaned_data['name']
            # set new accountType's order to last place
            accountType.order = AccountType.objects.all().aggregate(Max('order'))['order__max'] + 1
            accountType.sign = parseAccountTypeSign(form.cleaned_data['sign'])
            accountType.save()
            return redirect(reverse('benny:accountTypeRead', kwargs={ 'id': accountType.id }))
    # something must have gone wrong
    return redirect(reverse('benny:index'))

def accountTypeRead(request, id):
    # https://docs.djangoproject.com/en/1.10/intro/tutorial04/
    # in 'objects.get', pass pk=id as search criteria
    accountType = AccountType.objects.get(user=request.user, pk=id)
    
    accounts = Account.objects.filter(user=request.user, accountType=accountType).order_by('order', 'name')
    accountSummaries = summarizeAccounts(accounts, parse_from_date(request), parse_to_date(request))
    return render(request, 'benny/accountTypeRead.html',
                  { 'accountType': accountType,
                    'accountSummaries': accountSummaries, })

def accountTypeUpdate(request, id):
    accountType = AccountType.objects.get(user=request.user, pk=id)
    form = AccountTypeForm(instance=accountType)
    return render(request, 'benny/accountTypeUpdate.html', { 'form': form, 'id': id })

def accountTypeSaveUpdate(request, id):
    if request.method == "POST":
        form = AccountTypeForm(request.POST)
        if form.is_valid():
            accountType = AccountType.objects.get(user=request.user, pk=id)
            accountType.name = form.cleaned_data['name']
            accountType.sign = parseAccountTypeSign(form.cleaned_data['sign'])
            accountType.save()
    return redirect(reverse('benny:accountTypeRead', kwargs={ 'id': id }))

def accountTypeConfirmDelete(request, id):
    accountType = AccountType.objects.get(user=request.user, pk=id)
    prevUrl = request.GET.get('prev', reverse('benny:accountTypeRead', kwargs={ 'id': id }))
    nextUrl = reverse('benny:accountTypeDelete', kwargs={ 'id': id }) + "?next=" + prevUrl
    if not is_safe_url(prevUrl):
        prev = reverse('benny:accountTypeRead', kwargs={ 'id': id })
    return render(request, 'benny/accountTypeConfirmDelete.html',
                  { 'accountType': accountType,
                    'prevUrl': prevUrl,
                    'nextUrl': nextUrl, })

def accountTypeDelete(request, id):
    accountType = AccountType.objects.get(user=request.user, pk=id)
    accountType.delete()
    return redirect(reverse('benny:index'))

###########
# Account #
###########

def accountCreate(request):
    pass

def accountSaveCreate(request):
    pass

def accountRead(request, id):
    pass

def accountUpdate(request, id):
    pass

def accountSaveUpdate(request, id):
    pass

def accountConfirmDelete(request, id):
    pass

def accountDelete(request, id):
    pass

###############
# Transaction #
###############

def transactionCreate(request):
    pass

def transactionSaveCreate(request):
    pass

def transactionRead(request, id):
    pass

def transactionUpdate(request, id):
    pass

def transactionSaveUpdate(request, id):
    pass

def transactionConfirmDelete(request, id):
    pass

def transactionDelete(request, id):
    pass

def transactionBulkDelete(request):
    # request.GET.getlist()
    pass
