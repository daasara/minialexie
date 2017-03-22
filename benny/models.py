import datetime
from math import ceil
from decimal import Decimal

from django.db import models, transaction
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.core.exceptions import ObjectDoesNotExist

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

def saveTxn(user, desc, amount, debit, credit, year, month, day):
    t = Transaction(user=user, description=desc, amount=Decimal(str(amount)), debit=debit, credit=credit, date=datetime.date(year, month, day))
    t.save()
        
# reset demo data
@transaction.atomic
def resetDemoData(sender, user, request, **kwargs):
    try:
        demoUser = User.objects.get(username="demo")
        if user == demoUser:
            # delete account types
            existingAccountTypes = AccountType.objects.filter(user=demoUser)
            existingAccountTypes.delete()

            # create typical account types
            assets = AccountType(user=demoUser, name='Assets', sign=1, order=1)
            expenses = AccountType(user=demoUser, name='Expenses', sign=1, order=2)
            liabilities = AccountType(user=demoUser, name='Liabilities', sign=-1, order=3)
            income = AccountType(user=demoUser, name='Income', sign=-1, order=4)
            equity = AccountType(user=demoUser, name='Equity', sign=-1, order=5)

            assets.save()
            expenses.save()
            liabilities.save()
            income.save()
            equity.save()
            
            # create typical accounts

            # Assets
            wallet = Account(accountType=assets, user=demoUser, name='Wallet', budget=0, order=1)
            wallet.save()
        
            checking = Account(accountType=assets, user=demoUser, name='Checking', budget=0, order=1)
            checking.save()
        
            savings = Account(accountType=assets, user=demoUser, name='Savings', budget=0, order=1)
            savings.save()
        
            # Expenses
            groceries = Account(accountType=expenses, user=demoUser, name='Groceries', budget=0, order=1)
            groceries.save()
        
            utilities = Account(accountType=expenses, user=demoUser, name='Utilities', budget=0, order=1)
            utilities.save()
        
            restaurants = Account(accountType=expenses, user=demoUser, name='Restaurants', budget=0, order=1)
            restaurants.save()
        
            movies = Account(accountType=expenses, user=demoUser, name='Movies', budget=0, order=1)
            movies.save()
    
            clothing = Account(accountType=expenses, user=demoUser, name='Clothing', budget=0, order=1)
            clothing.save()

            automotive = Account(accountType=expenses, user=demoUser, name='Automotive', budget=0, order=1)
            automotive.save()

            rent = Account(accountType=expenses, user=demoUser, name='Rent', budget=0, order=1)
            rent.save()
    
            # Liabilities
            creditCard = Account(accountType=liabilities, user=demoUser, name='Credit card', budget=0, order=1)
            creditCard.save()
            
            # Income
            salary = Account(accountType=income, user=demoUser, name='Salary', budget=0, order=1)
            salary.save()
            
            # Equity
            opening = Account(accountType=equity, user=demoUser, name='Opening balance', budget=0, order=1)
            opening.save()

            # sample transactions
            openChecking = Transaction(user=demoUser, description="Opening balance", amount=Decimal("329.72"), debit=checking, credit=opening, date=datetime.date(2017, 3, 2))
            openChecking.save()

            openSavings = Transaction(user=demoUser, description="Opening balance", amount=Decimal("2921.34"), debit=savings, credit=opening, date=datetime.date(2017, 3, 2))
            openSavings.save()

            # using function saveTxn, with signature
            # saveTxn(user, desc, amount, debit, credit, year, month, day):
            saveTxn(demoUser, "Opening balance", 32.25, wallet, opening, 2017, 1, 1)
            saveTxn(demoUser, "January salary", 2650.20, checking, salary, 2017, 2, 1)
            saveTxn(demoUser, "Transfer", 620, savings, checking, 2017, 2, 2)
            saveTxn(demoUser, "Chinatown Dim Sum", 32.80, restaurants, creditCard, 2017, 3, 5)

            # sample data
            saveTxn(demoUser, "February salary", 2650.20, checking, salary, 2017, 3, 2)
            saveTxn(demoUser, "New tires", 320.95, automotive, checking, 2017, 3, 9)
            saveTxn(demoUser, "Transfer", 490, savings, checking, 2017, 3, 9)

            saveTxn(demoUser, "Oil change", 20, automotive, creditCard, 2017, 3, 12)
            saveTxn(demoUser, "Black jeans", 49.90, clothing, creditCard, 2017, 3, 14)
            saveTxn(demoUser, "Pay credit card", 100, creditCard, checking, 2017, 3, 15)
            saveTxn(demoUser, "Withdrawal", 300, wallet, checking, 2017, 2, 15)
            saveTxn(demoUser, "Band T-shirt", 15.50, clothing, checking, 2017, 2, 17)
            saveTxn(demoUser, "Chicken, rice", 9.23, groceries, wallet, 2017, 2, 19)
            saveTxn(demoUser, "Blockbuster action flick", 12, movies, wallet, 2017, 3, 1)
            saveTxn(demoUser, "Gas", 15.90, utilities, checking, 2017, 3, 3)
            saveTxn(demoUser, "Water", 12.30, utilities, checking, 2017, 3, 5)
            saveTxn(demoUser, "Electricity", 49.20, utilities, checking, 2017, 3, 5)

            # auto
            saveTxn(demoUser, "Tune-up", 35.50, automotive, creditCard, 2017, 2, 19)
            saveTxn(demoUser, "Air freshener", 3.9, automotive, wallet, 2017, 3, 5)
            saveTxn(demoUser, "Gas", 35.23, automotive, creditCard, 2017, 3, 4)

            # clothing
            saveTxn(demoUser, "Baseball cap", 15, clothing, wallet, 2017, 3, 1)
            saveTxn(demoUser, "Running shoes", 59.9, clothing, creditCard, 2017, 3, 5)
            saveTxn(demoUser, "Sweatshirt", 35.95, clothing, creditCard, 2017, 3, 12)

            # groceries
            saveTxn(demoUser, "Water and potatoes", 12.32, groceries, wallet, 2017, 3, 1)
            saveTxn(demoUser, "Cat food", 15.50, groceries, wallet, 2017, 3, 12)

            # movies
            saveTxn(demoUser, "Thriller", 16.90, movies, creditCard, 2017, 3, 4)
            saveTxn(demoUser, "Romantic comedy", 12.90, movies, creditCard, 2017, 3, 11)
            saveTxn(demoUser, "Cartoon", 16.90, movies, creditCard, 2017, 3, 18)

            # rent
            saveTxn(demoUser, "January rent", 400, rent, checking, 2017, 1, 5)
            saveTxn(demoUser, "February rent", 400, rent, checking, 2017, 2, 5)
            saveTxn(demoUser, "March rent", 400, rent, checking, 2017, 3, 5)

            # restaurants
            saveTxn(demoUser, "Sushi", 72.20, restaurants, creditCard, 2017, 3, 10)
            saveTxn(demoUser, "Ramen", 19.90, restaurants, creditCard, 2017, 3, 2)
            saveTxn(demoUser, "Tempura", 32.15, restaurants, wallet, 2017, 2, 15)

    except ObjectDoesNotExist:
        pass
        
# call resetDemoData after logging in
user_logged_in.connect(resetDemoData)
