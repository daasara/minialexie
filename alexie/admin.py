from django.contrib import admin

from .models import AccountType, Account, Transaction

# Register your models here.

admin.site.register(AccountType)
admin.site.register(Account)
admin.site.register(Transaction)
