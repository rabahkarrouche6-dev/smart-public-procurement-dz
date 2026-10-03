"""Procurements URL routes."""
from rest_framework.routers import DefaultRouter
from apps.procurements.views import ProcurementViewSet

router = DefaultRouter()
router.register(r'', ProcurementViewSet, basename='procurement')

urlpatterns = router.urls
