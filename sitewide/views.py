from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

def index(request):
    return HttpResponse("""
    <pre>
    Sitewide index

    <a href="/admin/">Admin</a>

    
    <a href="/alexie/">Alexie</a>
    
    """)

class UserProfile(TemplateView):
    template_name = "registration/user_profile.html"
