"""Evaluations URL routes."""
from rest_framework.routers import DefaultRouter
from apps.evaluations.views import EvaluationViewSet

router = DefaultRouter()
router.register(r'', EvaluationViewSet, basename='evaluation')

urlpatterns = router.urls
