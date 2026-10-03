"""Negative Security and Access Control Tests.
Verifies zero-trust tenant boundaries, role separation, sealed bid privacy, and FSM guardrails.
"""
import pytest
from rest_framework.test import APIClient
from decimal import Decimal
from django.core.exceptions import ValidationError, PermissionDenied
from apps.procurements.models import Procurement
from apps.procurements.services.transition_procurement import (
    transition_procurement,
    ProcurementWorkflowService,
)
from apps.audit.models import AuditLog
from apps.contracts.models import Contract
from apps.bids.models import Bid

@pytest.mark.django_db
def test_economic_operator_cannot_access_draft_procurement(sample_procurement, bidder_user):
    """Economic Operator must receive 404 when querying an un-published draft tender."""
    client = APIClient()
    client.force_authenticate(user=bidder_user)
    response = client.get(f"/api/v1/procurements/{sample_procurement.id}/")
    assert response.status_code == 404

@pytest.mark.django_db
def test_economic_operator_cannot_transition_procurement(sample_procurement, bidder_user):
    """Economic Operator attempting an FSM state transition must be rejected."""
    client = APIClient()
    client.force_authenticate(user=bidder_user)
    response = client.post(
        f"/api/v1/procurements/{sample_procurement.id}/transition/",
        {"target_status": Procurement.Status.PREPARATION, "reason": "Hacking attempt"}
    )
    # The API either returns 404 (because not in queryset) or 403
    assert response.status_code in [403, 404]

    with pytest.raises(PermissionDenied):
        ProcurementWorkflowService.transition(
            procurement=sample_procurement,
            target_status=Procurement.Status.PREPARATION,
            user=bidder_user
        )

@pytest.mark.django_db
def test_contracting_authority_cannot_access_central_admin_audit_logs(
    officer_user, central_admin_user, central_admin_org
):
    """Central Admin logs must never leak to a Contracting Authority officer."""
    # Create an audit event belonging exclusively to Central Admin
    admin_log = AuditLog.objects.create(
        actor=central_admin_user,
        actor_email=central_admin_user.email,
        organization=central_admin_org,
        action="SUPERVISORY_INSPECTION",
        resource_type="Organization",
        resource_id=str(central_admin_org.id)
    )

    # Officer checks audit logs
    officer_client = APIClient()
    officer_client.force_authenticate(user=officer_user)
    res_officer = officer_client.get("/api/v1/audit/logs/")
    assert res_officer.status_code == 200
    returned_ids = [item["id"] for item in res_officer.data.get("results", [])]
    assert str(admin_log.id) not in returned_ids

    # Central admin checks audit logs and sees it
    admin_client = APIClient()
    admin_client.force_authenticate(user=central_admin_user)
    res_admin = admin_client.get("/api/v1/audit/logs/")
    assert res_admin.status_code == 200
    admin_returned_ids = [item["id"] for item in res_admin.data.get("results", [])]
    assert str(admin_log.id) in admin_returned_ids

@pytest.mark.django_db
def test_economic_operator_cannot_access_audit_logs(bidder_user):
    """Economic Operators have zero access to platform audit logs."""
    client = APIClient()
    client.force_authenticate(user=bidder_user)
    response = client.get("/api/v1/audit/logs/")
    assert response.status_code == 200
    assert response.data.get("count", 0) == 0

@pytest.mark.django_db
def test_invalid_fsm_status_transition_rejected(sample_procurement, officer_user):
    """Disallowed transitions in the procurement lifecycle must raise ValidationError."""
    client = APIClient()
    client.force_authenticate(user=officer_user)
    
    # Attempting to jump directly from DRAFT to CLOSED
    response = client.post(
        f"/api/v1/procurements/{sample_procurement.id}/transition/",
        {"target_status": Procurement.Status.CLOSED}
    )
    assert response.status_code in [400, 422]

    # Service-level check
    with pytest.raises(ValidationError):
        ProcurementWorkflowService.transition(
            procurement=sample_procurement,
            target_status=Procurement.Status.CLOSED,
            user=officer_user
        )

@pytest.mark.django_db
def test_unauthenticated_requests_rejected(sample_procurement):
    """Unauthenticated access to protected endpoints must be strictly blocked with 401."""
    client = APIClient()
    res1 = client.get(f"/api/v1/procurements/{sample_procurement.id}/")
    assert res1.status_code == 401

    res2 = client.get("/api/v1/contracts/")
    assert res2.status_code == 401

    res3 = client.get("/api/v1/audit/logs/")
    assert res3.status_code == 401
