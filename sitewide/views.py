from django.shortcuts import render
from django.views.generic import TemplateView

class UserProfile(TemplateView):
    template_name = "registration/user_profile.html"
