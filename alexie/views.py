from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect

from .models import AccountType, Account, Transaction
from .forms import AccountTypeForm, TransactionForm
from .util import parse_from_date, parse_to_date, parse_amount
    
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

# AccountType

def accountTypeCreate(request):
    form = AccountTypeForm()
    return render(request, 'alexie/accountTypeCreate.html', { 'form': form })
    
def accountTypeSave(request):
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
    pass
    
def accountTypeDelete(request, pk):
    pass

# Account

def accountCreate(request):
    pass

def accountSave(request):
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

def accountUpdate(request, pk):
    pass

def accountDelete(request, pk):
    pass
    
# Transaction

def transactionCreate(request):
    form = TransactionForm()
    accounts = Account.objects.filter(user=request.user).order_by('name')
    form.fields['debit'].queryset = accounts
    form.fields['credit'].queryset = accounts

    newestTransactions = Transaction.objects.filter(user=request.user).order_by('-created')[:25]
    return render(request, 'alexie/transactionCreate.html', { 'form': form, 'newestTransactions': newestTransactions })

def transactionSave(request):
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
    pass

def transactionUpdate(request, pk):
    pass
    
def transactionDelete(request, pk):
    pass
    
