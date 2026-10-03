"""Subscriptions URL routes."""
from django.urls import path
from apps.subscriptions.views import CurrentSubscriptionView

urlpatterns = [
    path('current/', CurrentSubscriptionView.as_view(), name='subscription-current'),
]
