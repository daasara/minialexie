from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User

from .models import AccountType, Account, Transaction

def typicalSetup(t):
    """Attach test data to target test 't'"""
    t.user = User.objects.create_user(username="ted", email="t@t.com", password="top_secret")
    
    t.assetAccountType = AccountType(user=t.user, name="Test Asset AccountType", sign=1)
    t.incomeAccountType = AccountType(user=t.user, name="Test Income AccountType", sign=-1)
    
    t.assetAccount = Account(user=t.user, account_type=t.assetAccountType, name="Test Asset Account")
    t.incomeAccount = Account(user=t.user, account_type=t.incomeAccountType, name="Test Income Account")

class AccountTests(TestCase):
    def setUp(self):
        typicalSetup(self)

    def test_add_single_transaction(self):
        incomeToAssetTxn = Transaction(user=self.user, description="Test Income to Asset", amount=100, debit=self.assetAccount, credit=self.incomeAccount)
        
        print(self.incomeToAssetTxn)
        self.assertEquals(self.assetAccount.balance(), 100)
        
    def test_empty_account(self):
        self.assertEquals(self.assetAccount.balance(), 0)
