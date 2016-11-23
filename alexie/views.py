from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect

from .models import AccountType, Account, Transaction
from .forms import AccountTypeForm, TransactionForm
from .util import parse_from_date, parse_to_date, parse_amount, display_amount
    
def index(request):
    """
    Display all account balances in the selected time period
    """
    
    # check if user is logged in
    if not request.user.is_authenticated():
        return redirect('/auth/login/')
        
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

# For every model

# create
# saveCreate
# read
# update
# saveUpdate
# confirmDelete
# delete
    
# AccountType

def accountTypeCreate(request):
    form = AccountTypeForm()
    return render(request, 'alexie/accountTypeCreate.html', { 'form': form })
    
def accountTypeSaveCreate(request):
    # check for POST data to save, redirect to Create in any case
    if request.method == "POST":
        form = AccountTypeForm(request.POST)
        
        if form.is_valid():
            accountType = AccountType()
            accountType.user = request.user
            accountType.name = form.cleaned_data['name']
            # prevent invalid input: nonzero and greater than or less than +/-1
            if form.cleaned_data['sign'] == 0:
                accountType.sign = 1
            else:
                accountType.sign = round(form.cleaned_data['sign'] / abs(form.cleaned_data['sign']))
            accountType.save()
            
    return HttpResponseRedirect(reverse('alexie:accountTypeCreate'))
    
def accountTypeRead(request, pk):
    pass
    
def accountTypeUpdate(request, pk):
    accountType = AccountType.objects.get(user=request.user, pk=pk)
    form = AccountTypeForm(instance=accountType)
    return render(request, 'alexie/accountTypeUpdate.html', { 'form': form, 'id': pk })

def accountTypeSaveUpdate(request, pk):
    if request.method == "POST":
        form = AccountTypeForm(request.POST)
        
        if form.is_valid():
            accountType = AccountType.objects.get(user=request.user, pk=pk)
            accountType.name = form.cleaned_data['name']
            accountType.sign = round(form.cleaned_data['sign'] / abs(form.cleaned_data['sign']))
            accountType.save()
            
    return HttpResponseRedirect(reverse('alexie:accountTypeCreate'))

def accountTypeConfirmDelete(request, pk):
    pass
    
def accountTypeDelete(request, pk):
    accountType = AccountType.objects.get(user=request.user, pk=pk)
    accountType.delete()
    return HttpResponseRedirect(reverse('alexie:index'))


# Account

def accountCreate(request):
    pass

def accountSaveCreate(request):
    pass

def accountRead(request, pk):
    from_date = parse_from_date(request)
    to_date = parse_to_date(request)
    
    account = Account.objects.get(user=request.user, pk=pk)
    transactions = Transaction.objects.filter(
        debit=account,
        created__gte=from_date,
        created__lte=to_date) | Transaction.objects.filter(
        credit=account,
        created__gte=from_date,
        created__lte=to_date)
            
    return render(request, "alexie/accountRead.html",
                  { 'id': pk,
                    'account': account,
                    'transactions': transactions })

def accountRead(request, pk):
    pass
    
def accountUpdate(request, pk):
    pass

def accountSaveUpdate(request, pk):
    pass

def accountConfirmDelete(request, pk):
    pass
    
def accountDelete(request, pk):
    account = Account.objects.get(user=request.user, pk=pk)
    account.delete()
    return HttpResponseRedirect(reverse('alexie:index'))
    
# Transaction

def transactionCreate(request):
    form = TransactionForm()
    accounts = Account.objects.filter(user=request.user).order_by('name')
    form.fields['debit'].queryset = accounts
    form.fields['credit'].queryset = accounts

    newestTransactions = Transaction.objects.filter(user=request.user).order_by('-created')[:25]
    return render(request, 'alexie/transactionCreate.html', { 'form': form, 'newestTransactions': newestTransactions })

def transactionSaveCreate(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        form.fields['debit'].queryset = Account.objects.filter(pk=request.POST['debit'])
        form.fields['credit'].queryset = Account.objects.filter(pk=request.POST['credit'])

        if form.is_valid():
            transaction = Transaction()
            transaction.user = request.user
            transaction.description = form.cleaned_data['description']
            transaction.amount = parse_amount(form.cleaned_data['amount'])
            transaction.debit = form.cleaned_data['debit']
            transaction.credit = form.cleaned_data['credit']
            transaction.created = form.cleaned_data['created']
            transaction.save()
    return HttpResponseRedirect(reverse('alexie:transactionCreate'))
    
def transactionRead(request, pk):
    # share template with transactionConfirmDelete
    pass

def transactionUpdate(request, pk):
    transaction = Transaction.objects.get(user=request.user, pk=pk)
    try:
        debit_id = transaction.debit.id
    except AttributeError:
        # will occur if Transaction belonged to a deleted account
        debit_id = ""

    try:
        credit_id = transaction.credit.id
    except AttributeError:
        credit_id = ""
        
    form = TransactionForm({ 'created': transaction.created,
                             'description': transaction.description,
                             'amount': display_amount(transaction.amount),
                             'debit': debit_id,
                             'credit': credit_id, })
    form.fields['debit'].queryset = Account.objects.filter(user=request.user)
    form.fields['credit'].queryset = Account.objects.filter(user=request.user)
    return render(request, 'alexie/transactionUpdate.html', { 'form': form, 'id': pk })

def transactionSaveUpdate(request, pk):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        form.fields['debit'].queryset = Account.objects.filter(user=request.user)
        form.fields['credit'].queryset = Account.objects.filter(user=request.user)
        
        if form.is_valid():
            transaction = Transaction.objects.get(user=request.user, pk=pk)
            transaction.description = form.cleaned_data['description']
            transaction.amount = parse_amount(form.cleaned_data['amount'])
            transaction.debit = form.cleaned_data['debit']
            transaction.credit = form.cleaned_data['credit']
            transaction.created = form.cleaned_data['created']
            transaction.save()
    return HttpResponseRedirect(reverse('alexie:transactionCreate'))

def transactionConfirmDelete(request, pk):
    # share template with transactionRead
    pass
    
def transactionDelete(request, pk):
    transaction = Transaction.objects.get(user=request.user, pk=pk)
    transaction.delete()
    # FIXME Redirect to previous page, most likely account view but could also be transactionRead
    return HttpResponseRedirect(reverse('alexie:accountRead'))
