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
            {'id': account.id,
             'name': account.name,
             'budget': budget,
             'datesBalance': datesBalance,
             'percentSpent': percentSpent})
    return accountSummaries

def parseAccountTypeSign(value):
    # Given a form's value, return +/-1
    if value == 0:
        return 1
    else:
        return round(value / abs(value))

def nextOrderIndex(model, user):
    objects = model.objects.filter(user=user)
    if not objects:
        return 1
    else:
        return objects.aggregate(Max('order'))['order__max'] + 1
        
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

        # compute total for accountType
        accountType.total = sum([account['datesBalance'] for account in accountType.accountSummaries])

    return render(request, 'benny/index.html',
                  {'accountTypes': accountTypes})

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
    
    accounts = Account.objects.filter(user=request.user, accountType=accountType).order_by('order', 'name')
    accountSummaries = summarizeAccounts(accounts, parse_from_date(request), parse_to_date(request))
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
    prevUrl = request.GET.get('prev', reverse('benny:accountTypeRead', kwargs={'id': id}))
    nextUrl = reverse('benny:accountTypeDelete', kwargs={'id': id}) + "?next=" + prevUrl
    if not is_safe_url(prevUrl):
        prevUrl = reverse('benny:accountTypeRead', kwargs={'id': id})
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
    form.fields['accountType'].queryset = AccountType.objects.filter(user=request.user)

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
    from_date = parse_from_date(request)
    to_date = parse_to_date(request)
    
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
    userAccounts = Account.objects.filter(user=request.user)
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
