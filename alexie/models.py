from datetime import date

from django.db import models
from django.contrib.auth.models import User

# AccountType

# Account

# Transaction

class AccountType(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    sign = models.IntegerField()

    def __str__(self):
        return "%s (%s)" % (self.name, self.sign)

# repeat User ForeignKey for convenience, such as looking up all entries, or cascading delete

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_type = models.ForeignKey(AccountType, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    budget = models.IntegerField(default=0)

    def balance(self, from_date=date(1900, 1, 1), to_date=date(2100, 1, 1)):
        pass

    def __str__(self):
        return "%s" % self.name

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    amount = models.IntegerField()
    debit = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="debit_transactions")
    credit = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, related_name="credit_transactions")
    created = models.DateField("Creation date of transaction", default=date.today)

    def __str__(self):
        return "%s %s %s %s/%s" % (self.created, self.description, self.amount, self.debit, self.credit)
        
