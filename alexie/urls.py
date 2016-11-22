from django.conf.urls import url

from . import views

app_name = "alexie"

urlpatterns = [
    url(r'^$', views.index, name='index'),

    # AccountType
    url(r'^accounttype/create$', views.accounttypeCreate, name="accounttypeCreate"),
    url(r'^accounttype/read/(?P<pk>[0-9]+)$', views.accounttypeRead, name="accounttypeRead"),
    url(r'^accounttype/update/(?P<pk>[0-9]+)$', views.accounttypeUpdate, name="accounttypeUpdate"),
    url(r'^accounttype/delete/(?P<pk>[0-9]+)$', views.accounttypeDelete, name="accounttypedelete"),

    # Account
    #url(r'^$', views., name=""),
    url(r'^account/read/(?P<pk>[0-9]+)$', views.accountRead, name="account"),
    #url(r'^$', views., name=""),
    #url(r'^$', views., name=""),

    # Transaction
    url(r'^transaction/create$', views.transactionCreate, name="transactionCreate"),
    url(r'^transaction/save$', views.transactionSave, name="transactionSave"),
    #url(r'^$', views., name=""),
    #url(r'^$', views., name=""),
    #url(r'^$', views., name=""),
]
