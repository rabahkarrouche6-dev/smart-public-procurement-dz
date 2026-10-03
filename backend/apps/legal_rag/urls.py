"""Legal RAG URL routes."""
from rest_framework.routers import DefaultRouter
from apps.legal_rag.views import LegalArticleViewSet

router = DefaultRouter()
router.register(r'articles', LegalArticleViewSet, basename='legal-article')

urlpatterns = router.urls
