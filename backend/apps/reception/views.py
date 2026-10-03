"""Views and Serializers for Reception (PV)."""
from rest_framework import serializers, viewsets, permissions
from apps.reception.models import ReceptionRecord

class ReceptionRecordSerializer(serializers.ModelSerializer):
    reception_type_display = serializers.CharField(source='get_reception_type_display', read_only=True)
    decision_display = serializers.CharField(source='get_decision_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ReceptionRecord
        fields = [
            'id', 'organization', 'contract', 'reception_type', 'reception_type_display',
            'status', 'status_display', 'pv_number', 'reception_date', 'decision',
            'decision_display', 'reservations_text', 'guarantee_release_approved', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ReceptionViewSet(viewsets.ModelViewSet):
    serializer_class = ReceptionRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user or not user.is_authenticated:
            return ReceptionRecord.objects.none()
        if user.is_central_admin or user.is_superuser:
            return ReceptionRecord.objects.all()
        return ReceptionRecord.objects.filter(contract__organization=user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
