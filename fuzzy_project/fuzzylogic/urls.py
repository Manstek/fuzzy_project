# fuzzy_logic/urls.py
from django.urls import path
from .views import execute_logic

urlpatterns = [
    path('', execute_logic, name='fuzzy_logic'),
]
