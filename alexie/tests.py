from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User

from .models import AccountType, Account, Transaction

def typicalSetup(t):
    """Attach test data to target test 't'"""
    t.user = User.objects.create_user(username="ted", email="t@t.com", password="top_secret")
    t.user.save()
    
    t.assetAccountType = AccountType(user=t.user, name="Test Asset AccountType", sign=1)
    t.incomeAccountType = AccountType(user=t.user, name="Test Income AccountType", sign=-1)
    t.expenseAccountType = AccountType(user=t.user, name="Test Expense AccountType", sign=1)
    
    t.assetAccountType.save()
    t.incomeAccountType.save()
    t.expenseAccountType.save()
    
    t.assetAccount = Account(user=t.user, account_type=t.assetAccountType, name="Test Asset Account")
    t.incomeAccount = Account(user=t.user, account_type=t.incomeAccountType, name="Test Income Account")
    t.expenseAccount = Account(user=t.user, account_type=t.expenseAccountType, name="Test Expense Account")
    
    t.assetAccount.save()
    t.incomeAccount.save()
    t.expenseAccount.save()

class AccountTests(TestCase):
    def setUp(self):
        typicalSetup(self)

    def test_empty_account(self):
        self.assertEquals(self.assetAccount.balance(), 0)

    def test_add_single_transaction(self):
        incomeToAssetTxn = Transaction(user=self.user, description="Test Income to Asset", amount=100, debit=self.assetAccount, credit=self.incomeAccount)
        incomeToAssetTxn.save()

        self.assertEquals(self.assetAccount.balance(), 100)
        
    def test_add_two_transactions(self):
        salary = Transaction(user=self.user, description="Test Salary", amount=2000, debit=self.assetAccount, credit=self.incomeAccount)
        salary.save()

        lunch = Transaction(user=self.user, description="Test Lunch", amount=10, debit=self.expenseAccount, credit=self.assetAccount)
        lunch.save()

        self.assertEquals(self.incomeAccount.balance(), 2000)
        self.assertEquals(self.expenseAccount.balance(), 10)
        self.assertEquals(self.assetAccount.balance(), 1990)
