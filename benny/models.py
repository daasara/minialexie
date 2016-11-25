import datetime
from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User

class AccountType(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    sign = models.IntegerField()
    
    # used for left-to-right ordering in display (view)
    order = models.IntegerField()  

    def __str__(self):
        return "%s (%s) nth: %s" % (self.name, self.sign, self.order)

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accountType = models.ForeignKey(AccountType, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=100)
    budget = models.DecimalField(max_digits=22, decimal_places=2, default=Decimal(0))

    # order is relative to other accounts in the same account type. When moving accounts to another type, must place last in sequence
    order = models.IntegerField()

    def balance(self, from_date=datetime.date(1900, 1, 1), to_date=datetime.date(2100, 1, 1)):
        total = Decimal(0)
        debit_transactions = self.debit_transactions.filter(date__gte=from_date, date__lte=to_date)
        credit_transactions = self.credit_transactions.filter(date__gte=from_date, date__lte=to_date)

        for debit in debit_transactions:
            total += self.accountType.sign * debit.amount
        for credit in credit_transactions:
            total -= self.accountType.sign * credit.amount
        return total

    def __str__(self):
        return "%s nth: %s" % (self.name, self.order)

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=22, decimal_places=2)
    debit = models.ForeignKey(Account, on_delete=models.SET_NULL, blank=True, null=True, related_name="debit_transactions")
    credit = models.ForeignKey(Account, on_delete=models.SET_NULL, blank=True, null=True, related_name="credit_transactions")
    date = models.DateField("Date of transaction", default=datetime.date.today)

    def __str__(self):
        return "%s %s %s %s/%s" % (self.date, self.description, self.amount, self.debit, self.credit)
