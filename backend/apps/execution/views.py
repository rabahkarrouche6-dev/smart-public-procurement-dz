"""Views and Serializers for Execution, ODS, Milestones, Progress, and Payments."""
from rest_framework import serializers, viewsets, permissions
from apps.execution.models import ServiceOrder, ExecutionMilestone, ProgressRecord, PaymentRecord

class ServiceOrderSerializer(serializers.ModelSerializer):
    ods_type_display = serializers.CharField(source='get_ods_type_display', read_only=True)
    class Meta:
        model = ServiceOrder
        fields = ['id', 'organization', 'contract', 'ods_number', 'ods_type', 'ods_type_display', 'issue_date', 'effective_date', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']

class ExecutionMilestoneSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    class Meta:
        model = ExecutionMilestone
        fields = ['id', 'organization', 'contract', 'title', 'target_completion_date', 'actual_completion_date', 'status', 'status_display', 'progress_percentage', 'created_at']
        read_only_fields = ['id', 'created_at']

class ProgressRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressRecord
        fields = ['id', 'organization', 'contract', 'record_number', 'record_date', 'physical_progress_percentage', 'financial_progress_percentage', 'cumulative_amount', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']

class PaymentRecordSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    class Meta:
        model = PaymentRecord
        fields = ['id', 'organization', 'contract', 'situation_number', 'period_start', 'period_end', 'amount_requested', 'amount_approved', 'status', 'status_display', 'payment_order_reference', 'created_at']
        read_only_fields = ['id', 'created_at']

class ServiceOrderViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user or not user.is_authenticated:
            return ServiceOrder.objects.none()
        if user.is_central_admin or user.is_superuser:
            return ServiceOrder.objects.all()
        return ServiceOrder.objects.filter(contract__organization=user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

class ExecutionMilestoneViewSet(viewsets.ModelViewSet):
    serializer_class = ExecutionMilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user or not user.is_authenticated:
            return ExecutionMilestone.objects.none()
        if user.is_central_admin or user.is_superuser:
            return ExecutionMilestone.objects.all()
        return ExecutionMilestone.objects.filter(contract__organization=user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

class ProgressRecordViewSet(viewsets.ModelViewSet):
    serializer_class = ProgressRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user or not user.is_authenticated:
            return ProgressRecord.objects.none()
        if user.is_central_admin or user.is_superuser:
            return ProgressRecord.objects.all()
        return ProgressRecord.objects.filter(contract__organization=user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

class PaymentRecordViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user or not user.is_authenticated:
            return PaymentRecord.objects.none()
        if user.is_central_admin or user.is_superuser:
            return PaymentRecord.objects.all()
        return PaymentRecord.objects.filter(contract__organization=user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
