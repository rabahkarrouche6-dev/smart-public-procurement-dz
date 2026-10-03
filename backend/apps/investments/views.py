"""Views and Serializers for Investments, Envelopes, Programs, and Budgets."""
from rest_framework import serializers, viewsets, permissions
from apps.investments.models import Budget, InvestmentEnvelope, InvestmentProgram, InvestmentOperation

class BudgetSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    class Meta:
        model = Budget
        fields = ['id', 'organization', 'organization_name', 'fiscal_year', 'initial_allocation', 'current_allocation', 'committed_amount', 'created_at']
        read_only_fields = ['id', 'created_at']

class InvestmentEnvelopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentEnvelope
        fields = ['id', 'organization', 'budget', 'code', 'title', 'allocated_amount', 'consumed_amount', 'created_at']
        read_only_fields = ['id', 'created_at']

class InvestmentProgramSerializer(serializers.ModelSerializer):
    program_type_display = serializers.CharField(source='get_program_type_display', read_only=True)
    class Meta:
        model = InvestmentProgram
        fields = ['id', 'organization', 'envelope', 'code', 'title', 'program_type', 'program_type_display', 'allocated_amount', 'created_at']
        read_only_fields = ['id', 'created_at']

class InvestmentOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentOperation
        fields = ['id', 'organization', 'operation_number', 'title', 'budget', 'program', 'program_authorization', 'payment_credits', 'created_at']
        read_only_fields = ['id', 'created_at']

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user or not user.is_authenticated:
            return Budget.objects.none()
        if user.is_central_admin or user.is_superuser:
            return Budget.objects.all()
        return Budget.objects.filter(organization=user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

class InvestmentEnvelopeViewSet(viewsets.ModelViewSet):
    serializer_class = InvestmentEnvelopeSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user or not user.is_authenticated:
            return InvestmentEnvelope.objects.none()
        if user.is_central_admin or user.is_superuser:
            return InvestmentEnvelope.objects.all()
        return InvestmentEnvelope.objects.filter(organization=user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

class InvestmentProgramViewSet(viewsets.ModelViewSet):
    serializer_class = InvestmentProgramSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user or not user.is_authenticated:
            return InvestmentProgram.objects.none()
        if user.is_central_admin or user.is_superuser:
            return InvestmentProgram.objects.all()
        return InvestmentProgram.objects.filter(organization=user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

class InvestmentOperationViewSet(viewsets.ModelViewSet):
    serializer_class = InvestmentOperationSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        if getattr(self, "swagger_fake_view", False) or not user or not user.is_authenticated:
            return InvestmentOperation.objects.none()
        if user.is_central_admin or user.is_superuser:
            return InvestmentOperation.objects.all()
        return InvestmentOperation.objects.filter(organization=user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
