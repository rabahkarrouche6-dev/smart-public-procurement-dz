"""Serializers and Views for Bid submissions and fold opening."""
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.bids.models import Bid
from apps.procurements.models import Procurement
from apps.audit.services import record_audit_event

class BidSerializer(serializers.ModelSerializer):
    bidder_name = serializers.CharField(source='bidder.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    procurement_title = serializers.CharField(source='procurement.title', read_only=True)

    class Meta:
        model = Bid
        fields = [
            'id', 'procurement', 'procurement_title', 'bidder', 'bidder_name',
            'submitted_by', 'status', 'status_display', 'financial_amount',
            'execution_delay_days', 'technical_offer_doc', 'financial_offer_doc',
            'administrative_doc', 'submitted_at', 'is_opened', 'opening_timestamp',
            'technical_score', 'financial_score', 'total_score', 'ranking',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'bidder', 'submitted_by', 'submitted_at', 'is_opened',
            'opening_timestamp', 'technical_score', 'financial_score', 'total_score',
            'ranking', 'created_at', 'updated_at'
        ]

class BidViewSet(viewsets.ModelViewSet):
    """
    Bid submissions and opening API.
    Enforces sealed folds and deadline locks.
    """
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'procurement']

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Bid.objects.none()

        if user.is_central_admin or user.is_superuser:
            return Bid.objects.all().select_related('bidder', 'procurement')

        if user.is_economic_operator:
            # Bidders see only their own bids
            return Bid.objects.filter(bidder=user.organization).select_related('bidder', 'procurement')

        if user.is_contracting_authority:
            # Contracting authority sees bids for their procurements
            # But confidential details remain sealed until OPENING
            return Bid.objects.filter(
                procurement__organization=user.organization
            ).select_related('bidder', 'procurement')

        return Bid.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_economic_operator and not user.is_superuser:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("فقط المتعاملون الاقتصاديون يمكنهم تقديم العروض.")

        procurement = serializer.validated_data['procurement']
        if procurement.status != Procurement.Status.BID_SUBMISSION:
            from rest_framework.exceptions import ValidationError as DRFValidationError
            raise DRFValidationError("لا يمكن إيداع العرض؛ مرحلة إيداع العروض ليست مفتوحة حالياً.")

        if procurement.submission_deadline and timezone.now() > procurement.submission_deadline:
            from rest_framework.exceptions import ValidationError as DRFValidationError
            raise DRFValidationError("انقضى الأجل الأقصى المحدد لإيداع العروض قانونياً.")

        bid = serializer.save(
            bidder=user.organization,
            submitted_by=user,
            status=Bid.Status.SUBMITTED,
            submitted_at=timezone.now()
        )

        record_audit_event(
            action='BID_SUBMITTED',
            resource_type='Bid',
            resource_id=str(bid.id),
            actor=user,
            organization=user.organization,
            request=self.request
        )

    @action(detail=True, methods=['post'], url_path='open-fold')
    def open_fold(self, request, pk=None):
        """Official fold opening during opening session."""
        bid = self.get_object()
        user = request.user

        if not user.is_contracting_authority and not user.is_superuser:
            return Response({'error': 'غير مصرح'}, status=status.HTTP_403_FORBIDDEN)

        if bid.procurement.status != Procurement.Status.OPENING:
            return Response(
                {'error': 'لا يمكن فتح الأظرفة إلا خلال جلسة فتح الأظرفة الرسمية.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        bid.is_opened = True
        bid.opening_timestamp = timezone.now()
        bid.status = Bid.Status.OPENED
        bid.save(update_fields=['is_opened', 'opening_timestamp', 'status', 'updated_at'])

        record_audit_event(
            action='BID_FOLD_OPENED',
            resource_type='Bid',
            resource_id=str(bid.id),
            actor=user,
            organization=bid.procurement.organization,
            request=request
        )

        return Response(BidSerializer(bid).data)
