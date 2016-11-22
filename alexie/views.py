from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect

from .models import AccountType, Account, Transaction
from .forms import TransactionForm
from .util import parse_from_date, parse_to_date
    
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

def accounttypeCreate(request):
    pass
    
def accounttypeSave(request):
    # check for POST data to save, redirect to Create in any case
    pass
    
def accounttypeRead(request, pk):
    pass
    
def accounttypeUpdate(request, pk):
    pass
    
def accounttypeDelete(request, pk):
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
            
    return render(request, "alexie/account.html",
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
    accounts = Account.objects.filter(user=request.user)
    form.fields['debit'].queryset = accounts
    form.fields['credit'].queryset = accounts

    newestTransactions = Transaction.objects.filter(user=request.user).order_by('-created')[:25]
    return render(request, 'alexie/transactionCreate.html', { 'form': form, 'newestTransactions': newestTransactions })

def transactionSave(request):
    if request.method == "POST":
        # return HttpResponse("In Save : got POST")
        form = TransactionForm(request.POST)
        form.fields['debit'].queryset = Account.objects.filter(pk=request.POST['debit'])
        form.fields['credit'].queryset = Account.objects.filter(pk=request.POST['credit'])
        #print(form)
        if form.is_valid():
            transaction = Transaction()
            transaction.user = request.user
            transaction.description = form.cleaned_data['description']
            transaction.amount = form.cleaned_data['amount']
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
    
