from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView

def index(request):
    return redirect(reverse('benny:index'))
    
class UserProfile(TemplateView):
    template_name = "registration/user_profile.html"
