"""Views and Serializers for Immutable Audit Logs."""
from rest_framework import serializers, viewsets, permissions
from apps.audit.models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = [
            'id', 'actor', 'actor_email', 'organization', 'action',
            'resource_type', 'resource_id', 'old_values', 'new_values',
            'correlation_id', 'ip_address', 'result', 'created_at'
        ]

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only view for audit logs.
    Modifications and deletions are blocked by design.
    """
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['action', 'resource_type', 'result']
    search_fields = ['resource_id', 'actor_email', 'correlation_id']
    ordering_fields = ['created_at']

    def get_queryset(self):
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user or not user.is_authenticated:
            return AuditLog.objects.none()
        if user.is_central_admin or user.is_superuser or getattr(user, 'role', '') == 'AUDITOR':
            return AuditLog.objects.all()
        if user.is_economic_operator:
            return AuditLog.objects.none()
        if user.organization:
            return AuditLog.objects.filter(organization=user.organization)
        return AuditLog.objects.none()
