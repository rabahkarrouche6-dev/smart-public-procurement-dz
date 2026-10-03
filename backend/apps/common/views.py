"""Template view for the frontend portal."""
from django.views.generic import TemplateView
from django.urls import path

class FrontendPortalView(TemplateView):
    template_name = 'index.html'
