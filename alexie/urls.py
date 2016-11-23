from django.conf.urls import url

from . import views

app_name = "alexie"

urlpatterns = [
    url(r'^$', views.index, name='index'),

    # AccountType
    url(r'^accountType/create$', views.accountTypeCreate, name="accountTypeCreate"),
    url(r'^accountType/saveCreate$', views.accountTypeSaveCreate, name="accountTypeSaveCreate"),
    url(r'^accountType/read/(?P<pk>[0-9]+)$', views.accountTypeRead, name="accountTypeRead"),
    url(r'^accountType/update/(?P<pk>[0-9]+)$', views.accountTypeUpdate, name="accountTypeUpdate"),
    url(r'^accountType/saveUpdate/(?P<pk>[0-9]+)$', views.accountTypeSaveUpdate, name="accountTypeSaveUpdate"),
    url(r'^accountType/delete/(?P<pk>[0-9]+)$', views.accountTypeDelete, name="accountTypeDelete"),

    # Account
    #url(r'^$', views., name="accountCreate"),
    #url(r'^$', views., name="accountSaveCreate"),
    url(r'^account/read/(?P<pk>[0-9]+)$', views.accountRead, name="accountRead"),
    #url(r'^$', views., name=""),
    #url(r'^$', views., name=""),
    url(r'^account/delete/(?P<pk>[0-9]+)$', views.accountDelete, name="accountDelete"),

    # Transaction
    url(r'^transaction/create$', views.transactionCreate, name="transactionCreate"),
    url(r'^transaction/saveCreate$', views.transactionSaveCreate, name="transactionSaveCreate"),
    url(r'^transaction/update/(?P<pk>[0-9]+)$', views.transactionUpdate, name="transactionUpdate"),
    url(r'^transaction/saveUpdate/(?P<pk>[0-9]+)$', views.transactionSaveUpdate, name="transactionSaveUpdate"),
    url(r'^transaction/confirmDelete/(?P<pk>[0-9]+)$', views.transactionConfirmDelete, name="transactionConfirmDelete"),
]
