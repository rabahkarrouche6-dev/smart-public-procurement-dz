"""Serializers for Procurement entities and FSM transitions."""
from rest_framework import serializers
from apps.procurements.models import Procurement

class ProcurementSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    procedure_display = serializers.CharField(source='get_procedure_type_display', read_only=True)

    class Meta:
        model = Procurement
        fields = [
            'id', 'procurement_number', 'title', 'description', 'organization',
            'organization_name', 'project', 'procedure_type', 'procedure_display',
            'status', 'status_display', 'estimated_budget', 'currency',
            'publication_date', 'submission_deadline', 'opening_date', 'evaluation_date',
            'bid_validity_days', 'appeal_deadline', 'legal_source_reference', 'requires_tender_fee',
            'tender_fee_amount', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'created_by', 'created_at', 'updated_at']

class ProcurementTransitionSerializer(serializers.Serializer):
    target_status = serializers.ChoiceField(choices=Procurement.Status.choices)
    reason = serializers.CharField(required=False, allow_blank=True)
