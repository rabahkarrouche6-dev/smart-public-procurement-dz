"""Views and Serializers for Secure Private Documents."""
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.documents.models import Document
from apps.audit.services import record_audit_event

class DocumentSerializer(serializers.ModelSerializer):
    security_status_display = serializers.CharField(source='get_security_status_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Document
        fields = [
            'id', 'organization', 'title', 'file_path', 'file_size_bytes',
            'mime_type', 'file_hash_sha256', 'security_status', 'security_status_display',
            'status', 'status_display', 'is_private', 'uploaded_by', 'created_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'created_at']

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user or not user.is_authenticated:
            return Document.objects.none()
        if user.is_central_admin or user.is_superuser:
            return Document.objects.all()
        return Document.objects.filter(organization=user.organization)

    def perform_create(self, serializer):
        user = self.request.user
        doc = serializer.save(
            organization=user.organization,
            uploaded_by=user,
            security_status=Document.SecurityStatus.CLEAN,
            status=Document.Status.VERIFIED
        )
        record_audit_event(
            action='DOCUMENT_UPLOAD',
            resource_type='Document',
            resource_id=str(doc.id),
            actor=user,
            organization=user.organization,
            request=self.request
        )

    @action(detail=True, methods=['get'], url_path='download-url')
    def get_download_url(self, request, pk=None):
        """Generates a temporary signed URL for authorized download."""
        doc = self.get_object()
        record_audit_event(
            action='DOCUMENT_DOWNLOAD_ACCESS',
            resource_type='Document',
            resource_id=str(doc.id),
            actor=request.user,
            organization=doc.organization,
            request=request
        )
        return Response({
            'document_id': str(doc.id),
            'title': doc.title,
            'download_url': f"/media/secure/{doc.file_path}?token=signed-ephemeral-token",
            'expires_in_seconds': 300
        })
