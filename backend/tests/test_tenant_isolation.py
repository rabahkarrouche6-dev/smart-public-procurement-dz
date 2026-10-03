"""Tests for multi-tenant organization data isolation and IDOR prevention."""
import pytest
from rest_framework.test import APIClient
from apps.procurements.models import Procurement
from apps.procurements.services.transition_procurement import transition_procurement
from django.core.exceptions import PermissionDenied

@pytest.mark.django_db
def test_tenant_isolation_queryset_filtering(sample_procurement, officer_user, other_officer_user):
    # Officer from Alger sees the procurement
    client_alger = APIClient()
    client_alger.force_authenticate(user=officer_user)
    res_alger = client_alger.get(f"/api/v1/procurements/{sample_procurement.id}/")
    assert res_alger.status_code == 200
    assert res_alger.data["id"] == str(sample_procurement.id)

    # Officer from Oran must NOT see Alger's draft procurement
    client_oran = APIClient()
    client_oran.force_authenticate(user=other_officer_user)
    res_oran = client_oran.get(f"/api/v1/procurements/{sample_procurement.id}/")
    assert res_oran.status_code == 404

@pytest.mark.django_db
def test_cross_tenant_transition_prevented(sample_procurement, other_officer_user):
    # Direct service invocation attempt by a user from another organization
    with pytest.raises(PermissionDenied):
        transition_procurement(
            procurement=sample_procurement,
            target_status=Procurement.Status.PREPARATION,
            user=other_officer_user
        )
