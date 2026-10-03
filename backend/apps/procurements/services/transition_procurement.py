"""Deterministic Procurement Finite State Machine (FSM) Service."""
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
from apps.procurements.models import Procurement
from apps.audit.services import record_audit_event

ALLOWED_TRANSITIONS = {
    Procurement.Status.DRAFT: [Procurement.Status.PREPARATION, Procurement.Status.CANCELLED],
    Procurement.Status.PREPARATION: [Procurement.Status.APPROVAL, Procurement.Status.CANCELLED],
    Procurement.Status.APPROVAL: [Procurement.Status.PUBLICATION, Procurement.Status.PREPARATION, Procurement.Status.CANCELLED],
    Procurement.Status.PUBLICATION: [Procurement.Status.BID_SUBMISSION, Procurement.Status.CANCELLED],
    Procurement.Status.BID_SUBMISSION: [Procurement.Status.OPENING, Procurement.Status.CANCELLED],
    Procurement.Status.OPENING: [Procurement.Status.EVALUATION, Procurement.Status.CANCELLED],
    Procurement.Status.EVALUATION: [Procurement.Status.PROVISIONAL_AWARD, Procurement.Status.CANCELLED],
    Procurement.Status.PROVISIONAL_AWARD: [Procurement.Status.APPEAL, Procurement.Status.CANCELLED],
    Procurement.Status.APPEAL: [Procurement.Status.CONTRACT, Procurement.Status.PROVISIONAL_AWARD, Procurement.Status.CANCELLED],
    Procurement.Status.CONTRACT: [Procurement.Status.EXECUTION, Procurement.Status.CANCELLED],
    Procurement.Status.EXECUTION: [Procurement.Status.RECEPTION],
    Procurement.Status.RECEPTION: [Procurement.Status.CLOSED],
    Procurement.Status.CLOSED: [],
    Procurement.Status.CANCELLED: [],
}

def transition_procurement(
    procurement: Procurement,
    target_status: str,
    user,
    reason: str = "",
    request=None
) -> Procurement:
    """
    Executes an atomic and auditable FSM transition on a Procurement.
    Enforces authorization, preconditions, and records immutable audit log.
    """
    current_status = procurement.status

    # 1. Permission checks
    if not user or not user.is_authenticated:
        raise PermissionDenied("المستخدم غير مصرح له بتغيير حالة الصفقة.")

    if not user.is_contracting_authority and not user.is_superuser:
        raise PermissionDenied("فقط ممثلو المصلحة المتعاقدة المصرح لهم يمكنهم ترقية حالة الصفقة.")

    if procurement.organization_id != getattr(user, 'organization_id', None) and not user.is_superuser:
        raise PermissionDenied("لا يمكن تغيير حالة صفقة تابعة لهيئة أخرى (خرق العزل المؤسسي).")

    # 2. Check transition validity in state graph
    allowed = ALLOWED_TRANSITIONS.get(current_status, [])
    if target_status not in allowed:
        raise ValidationError(
            f"الانتقال غير مسموح قانونياً من الحالة '{procurement.get_status_display()}' إلى '{target_status}'."
        )

    # 3. Preconditions validation
    now = timezone.now()

    if target_status == Procurement.Status.PUBLICATION:
        if not procurement.publication_date:
            procurement.publication_date = now
        if not procurement.submission_deadline:
            raise ValidationError("لا يمكن نشر الإعلان دون تحديد الأجل الأقصى لإيداع العروض.")
        if procurement.submission_deadline <= procurement.publication_date:
            raise ValidationError("تاريخ إيداع العروض يجب أن يكون لاحقاً لتاريخ النشر.")

    elif target_status == Procurement.Status.OPENING:
        if procurement.submission_deadline and now < procurement.submission_deadline:
            raise ValidationError("لا يمكن فتح الأظرفة قبل انقضاء الأجل القانوني الأقصى لإيداع العروض.")

    # 4. Atomic execution & Audit trail
    with transaction.atomic():
        old_values = {'status': current_status}
        new_values = {'status': target_status, 'reason': reason}

        procurement.status = target_status
        procurement.save(update_fields=['status', 'publication_date', 'updated_at'])

        record_audit_event(
            action='PROCUREMENT_STATUS_TRANSITION',
            resource_type='Procurement',
            resource_id=str(procurement.id),
            actor=user,
            organization=procurement.organization,
            old_values=old_values,
            new_values=new_values,
            request=request
        )

    return procurement


class ProcurementWorkflowService:
    """
    Workflow service governing Algerian public procurement state changes.
    """
    @staticmethod
    def transition(
        procurement: Procurement,
        target_status: str,
        user,
        reason: str = "",
        request=None
    ) -> Procurement:
        return transition_procurement(
            procurement=procurement,
            target_status=target_status,
            user=user,
            reason=reason,
            request=request
        )
