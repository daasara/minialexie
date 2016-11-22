from django.conf.urls import url

from . import views

app_name = "alexie"

urlpatterns = [
    url(r'^$', views.index, name='index'),

    # AccountType
    url(r'^accountType/create$', views.accountTypeCreate, name="accountTypeCreate"),
    url(r'^accountType/save$', views.accountTypeSave, name="accountTypeSave"),
    url(r'^accountType/read/(?P<pk>[0-9]+)$', views.accountTypeRead, name="accountTypeRead"),
    url(r'^accountType/update/(?P<pk>[0-9]+)$', views.accountTypeUpdate, name="accountTypeUpdate"),
    url(r'^accountType/delete/(?P<pk>[0-9]+)$', views.accountTypeDelete, name="accountTypedelete"),

    # Account
    #url(r'^$', views., name="accountCreate"),
    #url(r'^$', views., name="accountSave"),
    url(r'^account/read/(?P<pk>[0-9]+)$', views.accountRead, name="accountRead"),
    #url(r'^$', views., name=""),
    #url(r'^$', views., name=""),

    # Transaction
    url(r'^transaction/create$', views.transactionCreate, name="transactionCreate"),
    url(r'^transaction/save$', views.transactionSave, name="transactionSave"),
    #url(r'^$', views., name=""),
    #url(r'^$', views., name=""),
    #url(r'^$', views., name=""),
]
