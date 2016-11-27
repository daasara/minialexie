import datetime
from math import ceil
from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in

class AccountType(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    sign = models.IntegerField()
    
    # used for left-to-right ordering in display (view)
    order = models.IntegerField()  

    def summarizeAccounts(self, from_date=datetime.date(1900, 1, 1), to_date=datetime.date(2100, 1, 1)):
        accountSummaries = []
        for account in self.account_set.all().order_by('name'):
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

    def __str__(self):
        # return "%s (%s) nth: %s" % (self.name, self.sign, self.order)
        return self.name

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accountType = models.ForeignKey(AccountType, on_delete=models.CASCADE, verbose_name="Account type")
    name = models.CharField(max_length=100)
    budget = models.DecimalField(max_digits=22, decimal_places=2, default=Decimal(0))

    # order is relative to other accounts in the same account type. When moving accounts to another type, must place last in sequence
    order = models.IntegerField()

    def balance(self, from_date=datetime.date(1900, 1, 1), to_date=datetime.date(2100, 1, 1)):
        total = Decimal('0.00')
        debit_transactions = self.debit_transactions.filter(date__gte=from_date, date__lte=to_date)
        credit_transactions = self.credit_transactions.filter(date__gte=from_date, date__lte=to_date)

        for debit in debit_transactions:
            total += self.accountType.sign * debit.amount
        for credit in credit_transactions:
            total -= self.accountType.sign * credit.amount
        return total

    def __str__(self):
        # return "%s nth: %s" % (self.name, self.order)
        return self.name

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=22, decimal_places=2)
    debit = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="debit_transactions")
    credit = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="credit_transactions")
    date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return "%s %s %s %s/%s" % (self.date, self.description, self.amount, self.debit, self.credit)

# reset demo data

def resetDemoData(sender, user, request, **kwargs):
    demoUser = User.objects.get(username="demo")

    # delete account types
    existingAccountTypes = AccountType.objects.filter(user=demoUser)
    existingAccountTypes.delete()

    # create typical account types
    AccountType(user=demoUser, name='Assets Demo', sign=1, order=1).save()

user_logged_in.connect(resetDemoData)
