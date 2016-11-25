from math import ceil

from django.urls import reverse
from django.shortcuts import render, redirect

from .models import AccountType, Account, Transaction
from .forms import AccountTypeForm, AccountForm, TransactionForm
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

# For every model, there are up to eight functions
#
#               AccountType   Account    Transaction
#        create     done
#    saveCreate     done
#          read     done
#        update     done
#    saveUpdate     done
# confirmDelete  
#        delete  
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
            accountType.order = AccountType.objects.count() + 1
            formSign = form.cleaned_data['sign']
            if formSign == 0:
                accountType.sign = 1
            else:
                formSign = form.cleaned_data['sign']
                accountType.sign = round(formSign / abs(formSign))  
            accountType.save()
    return redirect(reverse('benny:accountTypeCreate'))

def accountTypeRead(request, id):
    accountType = AccountType.objects.get(user=request.user, pk=id)
    return render(request, 'benny/accountTypeRead.html', { 'accountType': accountType })

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
            formSign = form.cleaned_data['sign']
            if formSign == 0:
                accountType.sign = 1
            else:
                accountType.sign = round(formSign / abs(formSign))
            accountType.save()
    return redirect(reverse('benny:accountTypeRead', kwargs={ 'id': id }))

def accountTypeConfirmDelete(request, id):
    pass

def accountTypeDelete(request, id):
    pass

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
    # get list
    pass
