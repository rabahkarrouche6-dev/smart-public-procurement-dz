"""Procurement ViewSet with multi-tenant filtering and FSM transition endpoint."""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.procurements.models import Procurement
from apps.procurements.serializers import ProcurementSerializer, ProcurementTransitionSerializer
from apps.procurements.services.transition_procurement import transition_procurement
from apps.accounts.permissions import IsContractingAuthority

class ProcurementViewSet(viewsets.ModelViewSet):
    """
    Procurement CRUD and FSM lifecycle transition API.
    Tenant-scoped:
    - Contracting Authorities manage their own tenders.
    - Economic Operators view published active tenders.
    - Central Admin oversees all tenders.
    """
    serializer_class = ProcurementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'procedure_type', 'organization']
    search_fields = ['procurement_number', 'title', 'description']
    ordering_fields = ['created_at', 'submission_deadline', 'estimated_budget']

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Procurement.objects.none()

        if user.is_central_admin or user.is_superuser:
            return Procurement.objects.all().select_related('organization', 'project')

        if user.is_contracting_authority:
            # Contracting authority sees their own procurements
            return Procurement.objects.filter(
                organization=user.organization
            ).select_related('organization', 'project')

        # Economic operators see only published/public procurements
        public_statuses = [
            Procurement.Status.PUBLICATION,
            Procurement.Status.BID_SUBMISSION,
            Procurement.Status.OPENING,
            Procurement.Status.EVALUATION,
            Procurement.Status.PROVISIONAL_AWARD,
            Procurement.Status.APPEAL,
            Procurement.Status.CONTRACT,
            Procurement.Status.CLOSED,
        ]
        return Procurement.objects.filter(
            status__in=public_statuses
        ).select_related('organization', 'project')

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_contracting_authority and not user.is_superuser:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("فقط المصلحة المتعاقدة تمتلك صلاحية إنشاء صفقة عمومية جديدة.")

        serializer.save(
            organization=user.organization,
            created_by=user,
            status=Procurement.Status.DRAFT
        )

    @action(detail=True, methods=['post'], url_path='transition')
    def execute_transition(self, request, pk=None):
        procurement = self.get_object()
        serializer = ProcurementTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_status = serializer.validated_data['target_status']
        reason = serializer.validated_data.get('reason', '')

        updated_procurement = transition_procurement(
            procurement=procurement,
            target_status=target_status,
            user=request.user,
            reason=reason,
            request=request
        )

        return Response(
            ProcurementSerializer(updated_procurement).data,
            status=status.HTTP_200_OK
        )
