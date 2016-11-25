from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url

from .models import AccountType, Account, Transaction
from .forms import AccountTypeForm, AccountForm, TransactionForm
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
    
    account_types = AccountType.objects.filter(user=request.user).order_by('name')
    account_type_names = {}
    
    accounts = {}
    account_names = {}
    account_balances = {}
    
    for account_type in account_types:
        account_type_names[account_type.id] = account_type.name
        accounts[account_type.id] = Account.objects.filter(account_type=account_type.id).order_by('name')
        for account in accounts[account_type.id]:
            account_names[account.id] = account.name
            account_balances[account.id] = account.balance(from_date, to_date)
        
    return render(request, "alexie/index.html",
                  { 'account_type_names': account_type_names,
                    'accounts': sorted(accounts.items()),
                    'account_names': account_names,
                    'account_balances': account_balances })

# For every model, there are eight functions

#               AccountType   Account    Transaction
#        create     done       done         done
#    saveCreate     done       done         done
#          read               sketch
#        update  needs link                 done
#    saveUpdate     done                    done
# confirmDelete                             done
#        delete  copy other  copy other     done
#    bulkDelete      not available       via checkboxes

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
    # Copy code in transactionDelete
    accountType = AccountType.objects.get(user=request.user, pk=pk)
    accountType.delete()
    return HttpResponseRedirect(reverse('alexie:index'))


# Account

def accountCreate(request):
    form = AccountForm()
    # Show only user's account types
    form.fields['account_type'].queryset = AccountType.objects.filter(user=request.user)
    return render(request, 'alexie/accountCreate.html', { 'form': form })

def accountSaveCreate(request):
    if request.method == "POST":
        form = AccountForm(request.POST)

        if form.is_valid():
            account_type = AccountType.objects.get(user=request.user, pk=form.cleaned_data['account_type'].id)
            account = Account()
            account.user = request.user
            account.account_type = account_type
            account.name = form.cleaned_data['name']
            account.budget = form.cleaned_data['budget']
            account.save()
    return HttpResponseRedirect(reverse('alexie:accountCreate'))

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
                    'transactions': transactions,
                    'prevUrl': reverse('alexie:accountRead', kwargs={ 'pk': pk }), })

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
    return render(request, 'alexie/transactionCreate.html',
                  { 'form': form,
                    'newestTransactions': newestTransactions,
                    'prevUrl': reverse('alexie:transactionCreate'), })

def transactionSaveCreate(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        form.fields['debit'].queryset = Account.objects.filter(user=request.user, pk=request.POST['debit'])
        form.fields['credit'].queryset = Account.objects.filter(user=request.user, pk=request.POST['credit'])

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
    # share detail template with transactionRead
    transaction = Transaction.objects.get(user=request.user, pk=pk)
    prevUrl = request.GET.get('prev', reverse('alexie:index'))
    nextUrl = reverse('alexie:transactionDelete', kwargs={ 'pk': pk }) + "?next=" + prevUrl
    if not is_safe_url(prevUrl):
        prev = reverse('alexie:index')
    return render(request, 'alexie/transactionConfirmDelete.html',
                  { 'transaction': transaction,
                    'prevUrl': prevUrl,
                    'nextUrl': nextUrl, })
    
def transactionDelete(request, pk):
    # http://stackoverflow.com/questions/35894990/django-how-to-return-to-previous-url
    next = request.GET.get('next', reverse('alexie:index'))
    transaction = Transaction.objects.get(user=request.user, pk=pk)
    transaction.delete()
    # Redirect to previous page, most likely account view but could also be transactionRead
    if not is_safe_url(next):
        next = reverse('alexie:index')
    return HttpResponseRedirect(next)
