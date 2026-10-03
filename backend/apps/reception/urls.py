"""Reception URL routes."""
from rest_framework.routers import DefaultRouter
from apps.reception.views import ReceptionViewSet

router = DefaultRouter()
router.register(r'', ReceptionViewSet, basename='reception')

urlpatterns = router.urls
