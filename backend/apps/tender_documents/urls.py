"""Tender Documents URL routes."""
from rest_framework.routers import DefaultRouter
from apps.tender_documents.views import TenderDocumentViewSet

router = DefaultRouter()
router.register(r'', TenderDocumentViewSet, basename='tender-document')

urlpatterns = router.urls
