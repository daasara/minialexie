import datetime
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User

from .models import AccountType, Account, Transaction

def typicalSetup(t):
    """Attach test data to target test 't'"""
    t.user = User.objects.create_user(username="ted", email="ted@ted.com", password="top_secret")
    t.user.save()

    t.assets = AccountType(user=t.user, name="Assets", sign=1, order=1)
    t.income = AccountType(user=t.user, name="Income", sign=-1, order=3)
    t.expenses = AccountType(user=t.user, name="Expenses", sign=1, order=2)

    t.assets.save()
    t.income.save()
    t.expenses.save()

    t.wallet = Account(user=t.user, accountType=t.assets, name="Wallet", budget=0, order=1)
    t.salary = Account(user=t.user, accountType=t.income, name="Salary", budget=0, order=1)
    t.groceries = Account(user=t.user, accountType=t.expenses, name="Groceries", budget=500, order=1)

    t.wallet.save()
    t.salary.save()
    t.groceries.save()

class AccountTests(TestCase):
    def setUp(self):
        typicalSetup(self)

    def test_empty_account(self):
        self.assertEquals(self.wallet.balance(), 0)

    def test_add_single_transaction(self):
        # add a salary transaction
        salaryTxn = Transaction(user=self.user, description="Salary", amount=2000, debit=self.wallet, credit=self.salary)
        salaryTxn.save()

        self.assertEquals(self.wallet.balance(), 2000)

    def test_add_two_transactions(self):
        salaryTxn = Transaction(user=self.user, description="Bigger salary", amount=7000, debit=self.wallet, credit=self.salary)
        dinnerTxn = Transaction(user=self.user, description="Rotisserie chicken", amount=15, debit=self.groceries, credit=self.wallet)
        salaryTxn.save()
        dinnerTxn.save()
        
        self.assertEquals(self.salary.balance(), 7000)
        self.assertEquals(self.wallet.balance(), 6985)
        self.assertEquals(self.groceries.balance(), 15)
