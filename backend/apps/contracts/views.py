"""Views and Serializers for Contracts and Milestones."""
from rest_framework import serializers, viewsets, permissions
from apps.contracts.models import Contract, ContractMilestone

class ContractMilestoneSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    class Meta:
        model = ContractMilestone
        fields = [
            'id', 'organization', 'contract', 'title', 'description',
            'due_date', 'status', 'status_display', 'weight_percentage', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ContractSerializer(serializers.ModelSerializer):
    contractor_name = serializers.CharField(source='contractor.name', read_only=True)
    milestones = ContractMilestoneSerializer(many=True, read_only=True)
    class Meta:
        model = Contract
        fields = [
            'id', 'contract_number', 'procurement', 'winning_bid', 'contractor',
            'contractor_name', 'contract_amount', 'performance_guarantee_amount',
            'status', 'signature_date', 'start_date', 'completion_delay_months',
            'milestones', 'created_at'
        ]

class ContractViewSet(viewsets.ModelViewSet):
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user or not user.is_authenticated:
            return Contract.objects.none()
        if user.is_central_admin or user.is_superuser:
            return Contract.objects.all().prefetch_related('milestones')
        if user.is_contracting_authority:
            return Contract.objects.filter(organization=user.organization).prefetch_related('milestones')
        return Contract.objects.filter(contractor=user.organization).prefetch_related('milestones')

class ContractMilestoneViewSet(viewsets.ModelViewSet):
    serializer_class = ContractMilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user or not user.is_authenticated:
            return ContractMilestone.objects.none()
        if user.is_central_admin or user.is_superuser:
            return ContractMilestone.objects.all()
        if user.is_contracting_authority:
            return ContractMilestone.objects.filter(organization=user.organization)
        return ContractMilestone.objects.filter(contract__contractor=user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
