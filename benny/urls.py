from django.conf.urls import url

from . import views

app_name = "benny"

urlpatterns = [
    url(r'^$', views.index, name='index'),

    # For every model

    # create
    # saveCreate  # avoid "confirm form resubmission" on browser reload
    # read
    # update
    # saveUpdate
    # confirmDelete
    # delete
    
    # AccountType

    url(r'^accountType/create$', views.accountTypeCreate, name="accountTypeCreate"),
    url(r'^accountType/saveCreate$', views.accountTypeSaveCreate, name="accountTypeSaveCreate"),
    url(r'^accountType/read/(?P<id>[0-9]+)$', views.accountTypeRead, name="accountTypeRead"),
    url(r'^accountType/update/(?P<id>[0-9]+)$', views.accountTypeUpdate, name="accountTypeUpdate"),
    url(r'^accountType/saveUpdate/(?P<id>[0-9]+)$', views.accountTypeSaveUpdate, name="accountTypeSaveUpdate"),
    url(r'^accountType/confirmDelete/(?P<id>[0-9]+)$', views.accountTypeConfirmDelete, name="accountTypeConfirmDelete"),
    url(r'^accountType/delete/(?P<id>[0-9]+)$', views.accountTypeDelete, name="accountTypeDelete"),

    # Account
    url(r'^account/create$', views.accountCreate, name="accountCreate"),
    url(r'^account/saveCreate$', views.accountSaveCreate, name="accountSaveCreate"),
    url(r'^account/read/(?P<id>[0-9]+)$', views.accountRead, name="accountRead"),
    url(r'^account/update/(?P<id>[0-9]+)$', views.accountUpdate, name="accountUpdate"),
    url(r'^account/saveUpdate/(?P<id>[0-9]+)$', views.accountSaveUpdate, name="accountSaveUpdate"),
    url(r'^account/confirmDelete/(?P<id>[0-9]+)$', views.accountConfirmDelete, name="accountConfirmDelete"),
    url(r'^account/delete/(?P<id>[0-9]+)$', views.accountDelete, name="accountDelete"),

    # Transaction
    url(r'^transaction/create$', views.transactionCreate, name="transactionCreate"),
    url(r'^transaction/saveCreate$', views.transactionSaveCreate, name="transactionSaveCreate"),
    url(r'^transaction/read/(?P<id>[0-9]+)$', views.transactionRead, name="transactionRead"),
    url(r'^transaction/update/(?P<id>[0-9]+)$', views.transactionUpdate, name="transactionUpdate"),
    url(r'^transaction/saveUpdate/(?P<id>[0-9]+)$', views.transactionSaveUpdate, name="transactionSaveUpdate"),
    url(r'^transaction/confirmDelete/(?P<id>[0-9]+)$', views.transactionConfirmDelete, name="transactionConfirmDelete"),
    url(r'^transaction/delete/(?P<id>[0-9]+)$', views.transactionDelete, name="transactionDelete"),

    url(r'^changeDates/$', views.changeDates, name="changeDates"),
    url(r'^presetDate/$', views.presetDate, name="presetDate"),

    url(r'^search/$', views.search, name="search"),
]
