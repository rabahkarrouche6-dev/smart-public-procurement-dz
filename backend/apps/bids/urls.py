"""Bids URL routes."""
from rest_framework.routers import DefaultRouter
from apps.bids.views import BidViewSet

router = DefaultRouter()
router.register(r'', BidViewSet, basename='bid')

urlpatterns = router.urls
