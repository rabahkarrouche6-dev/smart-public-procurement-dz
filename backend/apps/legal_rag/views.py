"""Views and Serializers for Legal RAG knowledge base."""
from rest_framework import serializers, viewsets, permissions
from apps.legal_rag.models import LegalDocument, LegalArticle

class LegalArticleSerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source='document.title', read_only=True)
    official_number = serializers.CharField(source='document.official_number', read_only=True)
    class Meta:
        model = LegalArticle
        fields = ['id', 'document', 'document_title', 'official_number', 'article_number', 'title', 'content_ar', 'content_fr', 'keywords']

class LegalDocumentSerializer(serializers.ModelSerializer):
    articles = LegalArticleSerializer(many=True, read_only=True)
    class Meta:
        model = LegalDocument
        fields = ['id', 'title', 'legal_type', 'official_number', 'promulgation_date', 'joradp_reference', 'status', 'articles']

class LegalArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """Search and view authoritative Algerian legal articles."""
    queryset = LegalArticle.objects.all().select_related('document')
    serializer_class = LegalArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['article_number', 'content_ar', 'content_fr', 'title']
    filterset_fields = ['document__official_number']
