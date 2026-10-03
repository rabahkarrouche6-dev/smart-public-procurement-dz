"""Views and Serializers for Tender Documents (DAO)."""
from rest_framework import serializers, viewsets, permissions
from apps.tender_documents.models import TenderDocument

class TenderDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderDocument
        fields = [
            'id', 'procurement', 'version', 'title', 'document', 'is_published',
            'content_hash', 'extracted_criteria', 'eligibility_conditions', 'created_at'
        ]

class TenderDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = TenderDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user or not user.is_authenticated:
            return TenderDocument.objects.none()
        if user.is_central_admin or user.is_superuser:
            return TenderDocument.objects.all()
        if user.is_contracting_authority:
            return TenderDocument.objects.filter(procurement__organization=user.organization)
        return TenderDocument.objects.filter(is_published=True)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
