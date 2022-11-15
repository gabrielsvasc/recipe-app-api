"""Urls para a rota User da API."""
from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateuserView.as_view(), name='create'),
]
