"""Serializers and views for Organizations."""
from rest_framework import serializers, viewsets, permissions
from apps.organizations.models import Organization

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'legal_representative', 'org_type', 'nif', 'registration_number', 'nis',
            'legal_status', 'wilaya_code', 'address', 'phone', 'email', 'website',
            'verification_status', 'data_provenance', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class OrganizationViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Organizations with tenant permissions.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['org_type', 'wilaya_code', 'verification_status']
    search_fields = ['name', 'nif', 'registration_number']
    ordering_fields = ['name', 'created_at']
