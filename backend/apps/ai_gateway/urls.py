"""AI Gateway URL routes."""
from django.urls import path
from apps.ai_gateway.views import AIQueryView

urlpatterns = [
    path('query/', AIQueryView.as_view(), name='ai-query'),
]
