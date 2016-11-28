from datetime import date, datetime
from calendar import monthrange
from math import ceil
from decimal import Decimal

from django.urls import reverse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url

from .models import AccountType, Account, Transaction
from .forms import AccountTypeForm, AccountForm, TransactionForm
from .util import parseDate, parseFromDate, parseToDate, displayDate
from .util import DEFAULT_FROM_DATE, DEFAULT_TO_DATE
from .util import parseAccountTypeSign, nextOrderIndex

def index(request):
    """
    Display all account balances in the selected time period.
    """
    if not request.user.is_authenticated():
        return redirect(reverse('login'))

    accountTypes = AccountType.objects.filter(user=request.user).order_by('order', 'name')

    fromDate = parseFromDate(request)
    toDate = parseToDate(request)

    for accountType in accountTypes:
        # retrieve balances here, using the parsed from and to dates
        accountType.accountSummaries = accountType.summarizeAccounts(fromDate, toDate)

        # compute total for accountType
        if len(accountType.accountSummaries) == 0:
            accountType.total = Decimal("0.00")
        else:
            accountType.total = sum([account['datesBalance'] for account in accountType.accountSummaries])

    return render(request, 'benny/index.html',
                  {'accountTypes': accountTypes,
                   'fromDate': displayDate(fromDate),
                   'toDate': displayDate(toDate)})

# For every model, there are up to eight functions
#
#               AccountType   Account    Transaction
#        create     done       done         done
#    saveCreate     done       done         done
#          read     done       done         done
#        update     done       done         done
#    saveUpdate     done       done         done
# confirmDelete     done       done         done
#        delete     done       done         done
# confirmBulkDl    ( not available ) 
#    bulkDelete    ( not available )    

###############
# AccountType #
###############

def accountTypeCreate(request):
    form = AccountTypeForm()
    return render(request, 'benny/accountTypeCreate.html',
                  {'form': form})

def accountTypeSaveCreate(request):
    if request.method == "POST":
        form = AccountTypeForm(request.POST)
        if form.is_valid():
            accountType = AccountType()
            accountType.user = request.user
            accountType.name = form.cleaned_data['name']
            # set new accountType's order to last place
            accountType.order = nextOrderIndex(AccountType, request.user)
            accountType.sign = parseAccountTypeSign(form.cleaned_data['sign'])
            accountType.save()
            # return redirect(reverse('benny:accountTypeRead', kwargs={'id': accountType.id}))
            return redirect(reverse('benny:index'))
    # if this point is reached, something must have gone wrong
    return redirect(reverse('benny:index'))

def accountTypeRead(request, id):
    # https://docs.djangoproject.com/en/1.10/intro/tutorial04/
    # in 'objects.get', use pk=id as search criteria
    accountType = AccountType.objects.get(user=request.user, pk=id)
    
    accounts = Account.objects.filter(user=request.user, accountType=accountType).order_by('name')  # order alphabetically
    accountSummaries = accountType.summarizeAccounts(parseFromDate(request), parseToDate(request))
    return render(request, 'benny/accountTypeRead.html',
                  {'accountType': accountType,
                   'accountSummaries': accountSummaries})

def accountTypeUpdate(request, id):
    accountType = AccountType.objects.get(user=request.user, pk=id)
    form = AccountTypeForm(instance=accountType)
    return render(request, 'benny/accountTypeUpdate.html', {'form': form, 'id': id})

def accountTypeSaveUpdate(request, id):
    if request.method == "POST":
        form = AccountTypeForm(request.POST)
        if form.is_valid():
            accountType = AccountType.objects.get(user=request.user, pk=id)
            accountType.name = form.cleaned_data['name']
            accountType.sign = parseAccountTypeSign(form.cleaned_data['sign'])
            accountType.save()
    # return redirect(reverse('benny:accountTypeRead', kwargs={'id': id}))
    return redirect(reverse('benny:index'))

def accountTypeConfirmDelete(request, id):
    accountType = AccountType.objects.get(user=request.user, pk=id)
    # if the GET parameter 'prev' is not set, send back to accountTypeRead
    prevUrl = request.GET.get('prev', reverse('benny:index'))
    nextUrl = reverse('benny:accountTypeDelete', kwargs={'id': id}) + "?next=" + prevUrl
    if not is_safe_url(prevUrl):
        prevUrl = reverse('benny:index')
    return render(request, 'benny/accountTypeConfirmDelete.html',
                  {'accountType': accountType,
                   'prevUrl': prevUrl,
                   'nextUrl': nextUrl})

def accountTypeDelete(request, id):
    accountType = AccountType.objects.get(user=request.user, pk=id)
    accountType.delete()
    return redirect(reverse('benny:index'))

###########
# Account #
###########

def accountCreate(request):
    # try auto-selecting account type
    accountTypeId = request.GET.get('accountType', "")

    form = AccountForm(initial={'accountType': accountTypeId})
    # Show only user's account types
    form.fields['accountType'].queryset = AccountType.objects.filter(user=request.user).order_by('order', 'name')  # order by index

    return render(request, 'benny/accountCreate.html', {'form': form})

def accountSaveCreate(request):
    if request.method == "POST":
        form = AccountForm(request.POST)
        if form.is_valid():
            # restrict to object belonging to user
            accountType = AccountType.objects.get(user=request.user, pk=form.cleaned_data['accountType'].id)
            
            account = Account()
            account.user = request.user
            account.accountType = accountType
            account.name = form.cleaned_data['name']
            account.budget = form.cleaned_data['budget']
            account.order = nextOrderIndex(Account, request.user)
            account.save()
            # return redirect(reverse('benny:accountTypeRead', kwargs={'id': accountType.id}))
            return redirect(reverse('benny:index'))
    # if this point is reached, something must have gone wrong
    return redirect(reverse('benny:index'))

def accountRead(request, id):
    account = Account.objects.get(user=request.user, pk=id)
    from_date = parseFromDate(request)
    to_date = parseToDate(request)
    
    transactions = Transaction.objects.filter(
        debit=account,
        date__gte=from_date,
        date__lte=to_date) | Transaction.objects.filter(
            credit=account,
            date__gte=from_date,
            date__lte=to_date)
    transactions = transactions.order_by('-date')

    return render(request, 'benny/accountRead.html',
                  {'account': account,
                   'accountBalance': account.balance(from_date, to_date),
                   'transactions': transactions})

def accountUpdate(request, id):
    account = Account.objects.get(user=request.user, pk=id)
    form = AccountForm(instance=account)
    form.fields['accountType'].queryset = AccountType.objects.filter(user=request.user)
    return render(request, 'benny/accountUpdate.html', {'id': id, 'form': form})

def accountSaveUpdate(request, id):
    if request.method == "POST":
        form = AccountForm(request.POST)
        if form.is_valid():
            accountType = AccountType.objects.get(user=request.user, pk=form.cleaned_data['accountType'].id)
            
            account = Account.objects.get(user=request.user, pk=id)
            account.accountType = accountType
            account.name = form.cleaned_data['name']
            account.budget = form.cleaned_data['budget']
            account.save()
    return redirect(reverse('benny:accountRead', kwargs={'id': id}))

def accountConfirmDelete(request, id):
    account = Account.objects.get(user=request.user, pk=id)
    prevUrl = request.GET.get('prev', reverse('benny:accountRead', kwargs={'id': id}))
    nextUrl = reverse('benny:accountDelete', kwargs={'id': id}) + "?next=" + prevUrl
    if not is_safe_url(prevUrl):
        prevUrl = reverse('benny:accountRead', kwargs={'id': id})
    return render(request, 'benny/accountConfirmDelete.html',
                  {'account': account,
                   'prevUrl': prevUrl,
                   'nextUrl': nextUrl})

def accountDelete(request, id):
    account = Account.objects.get(user=request.user, pk=id)
    account.delete()
    return redirect(reverse('benny:index'))

###############
# Transaction #
###############

def transactionCreate(request):
    form = TransactionForm()
    userAccounts = Account.objects.filter(user=request.user).order_by('name')
    form.fields['debit'].queryset = userAccounts
    form.fields['credit'].queryset = userAccounts
    return render(request, 'benny/transactionCreate.html', {'form': form})

def transactionSaveCreate(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            debit = Account.objects.get(user=request.user, pk=form.cleaned_data['debit'].id)
            credit = Account.objects.get(user=request.user, pk=form.cleaned_data['credit'].id)

            transaction = Transaction()
            transaction.user = request.user
            transaction.description = form.cleaned_data['description']
            transaction.amount = form.cleaned_data['amount']
            transaction.debit = debit
            transaction.credit = credit
            transaction.date = form.cleaned_data['date']
            transaction.save()
            return redirect(reverse('benny:transactionRead', kwargs={'id': transaction.id}))
    return redirect(reverse('benny:index'))

def transactionRead(request, id):
    transaction = Transaction.objects.get(user=request.user, pk=id)
    return render(request, 'benny/transactionRead.html', {'transaction': transaction})

def transactionUpdate(request, id):
    transaction = Transaction.objects.get(user=request.user, pk=id)
    form = TransactionForm(instance=transaction)
    userAccounts = Account.objects.filter(user=request.user)
    form.fields['debit'].queryset = userAccounts
    form.fields['credit'].queryset = userAccounts
    return render(request, 'benny/transactionUpdate.html', {'id': id, 'form': form})

def transactionSaveUpdate(request, id):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            debit = Account.objects.get(user=request.user, pk=form.cleaned_data['debit'].id)
            credit = Account.objects.get(user=request.user, pk=form.cleaned_data['credit'].id)
            
            transaction = Transaction.objects.get(user=request.user, pk=id)
            transaction.description = form.cleaned_data['description']
            transaction.amount = form.cleaned_data['amount']
            transaction.debit = debit
            transaction.credit = credit
            transaction.date = form.cleaned_data['date']
            transaction.save()
    return redirect(reverse('benny:transactionRead', kwargs={'id': id}))

def transactionConfirmDelete(request, id):
    transaction = Transaction.objects.get(user=request.user, pk=id)
    prevUrl = request.GET.get('prev', reverse('benny:transactionRead', kwargs={'id': id}))
    nextUrl = reverse('benny:transactionDelete', kwargs={'id': id}) + "?next=" + prevUrl
    if not is_safe_url(prevUrl):
        prevUrl = reverse('benny:transactionRead', kwargs={'id': id})
    return render(request, 'benny/transactionConfirmDelete.html',
                  {'transaction': transaction,
                   'prevUrl': prevUrl,
                   'nextUrl': nextUrl})

def transactionDelete(request, id):
    transaction = Transaction.objects.get(user=request.user, pk=id)
    transaction.delete()
    return redirect(reverse('benny:index'))

def transactionConfirmBulkDelete(request):
    # use checkboxes in accountRead, send to ConfirmBulkDelete, then to BulkDelete
    # use request.GET.getlist()
    pass
    
def transactionBulkDelete(request):
    pass

def changeDates(request):
    if request.method == "POST":
        fromDate = parseDate(request.POST['from'], DEFAULT_FROM_DATE)
        toDate = parseDate(request.POST['to'], DEFAULT_TO_DATE)

        # save parsed dates to session data
        request.session['fromDate'] = displayDate(fromDate)
        request.session['toDate'] = displayDate(toDate)
        
        if is_safe_url(request.POST['prevUrl']):
            return redirect(request.POST['prevUrl'])
    return redirect(reverse('benny:index'))

def presetDate(request):
    if request.method == "GET":
        choice = request.GET.get('choice', "allDates")
        today = date.today()
        if choice == "today":
            request.session['fromDate'] = displayDate(today)
            request.session['toDate'] = displayDate(today)
        elif choice == "month":
            monthDays = monthrange(today.year, today.month)
            request.session['fromDate'] = displayDate(date(today.year, today.month, 1))
            request.session['toDate'] = displayDate(date(today.year, today.month, monthDays[1]))
        elif choice == "year":
            request.session['fromDate'] = displayDate(date(today.year, 1, 1))
            request.session['toDate'] = displayDate(date(today.year, 12, 31))
        else:  # allDates
            request.session['fromDate'] = displayDate(DEFAULT_FROM_DATE)
            request.session['toDate'] = displayDate(DEFAULT_TO_DATE)
    prevUrl = request.GET.get('prevUrl', reverse('benny:index'))
    if is_safe_url(prevUrl):
        return redirect(prevUrl)
    else:
        return redirect(reverse('benny:index'))
    
def search(request):
    # render to account view
    pass
