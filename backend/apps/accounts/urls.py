"""Accounts API URL routes."""
from django.urls import path
from apps.accounts.views import RegisterView, LoginView, CurrentUserView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('me/', CurrentUserView.as_view(), name='auth-me'),
]
