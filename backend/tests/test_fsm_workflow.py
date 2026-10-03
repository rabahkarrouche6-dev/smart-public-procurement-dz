"""Tests for Procurement FSM lifecycle transitions and precondition rules."""
import pytest
from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
from apps.procurements.models import Procurement
from apps.procurements.services.transition_procurement import transition_procurement
from apps.audit.models import AuditLog

@pytest.mark.django_db
def test_valid_fsm_lifecycle_transitions(sample_procurement, officer_user):
    # DRAFT -> PREPARATION
    p1 = transition_procurement(sample_procurement, Procurement.Status.PREPARATION, officer_user)
    assert p1.status == Procurement.Status.PREPARATION

    # PREPARATION -> APPROVAL
    p2 = transition_procurement(p1, Procurement.Status.APPROVAL, officer_user)
    assert p2.status == Procurement.Status.APPROVAL

    # APPROVAL -> PUBLICATION (with deadlines set)
    p2.publication_date = timezone.now()
    p2.submission_deadline = timezone.now() + timezone.timedelta(days=21)
    p2.save()

    p3 = transition_procurement(p2, Procurement.Status.PUBLICATION, officer_user)
    assert p3.status == Procurement.Status.PUBLICATION

    # Verify audit log was recorded
    audit = AuditLog.objects.filter(resource_id=str(sample_procurement.id), action='PROCUREMENT_STATUS_TRANSITION').latest('created_at')
    assert audit.new_values['status'] == Procurement.Status.PUBLICATION
    assert audit.actor == officer_user

@pytest.mark.django_db
def test_invalid_fsm_jump_rejected(sample_procurement, officer_user):
    # Attempting to jump from DRAFT directly to CONTRACT
    with pytest.raises(ValidationError):
        transition_procurement(sample_procurement, Procurement.Status.CONTRACT, officer_user)

@pytest.mark.django_db
def test_economic_operator_cannot_transition_procurement(sample_procurement, bidder_user):
    with pytest.raises(PermissionDenied):
        transition_procurement(sample_procurement, Procurement.Status.PREPARATION, bidder_user)
