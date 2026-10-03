"""Pytest fixtures for Smart Public Procurement Platform."""
import pytest
from decimal import Decimal
from django.utils import timezone
from apps.organizations.models import Organization
from apps.accounts.models import User
from apps.procurements.models import Procurement
from apps.evaluations.models import EvaluationFormula, EvaluationCriterion
from apps.bids.models import Bid

@pytest.fixture
def contracting_org(db):
    """Sample contracting authority (Wilaya d'Alger)."""
    return Organization.objects.create(
        name="ولاية الجزائر - مديرية التجهيزات العمومية",
        org_type=Organization.OrgType.CONTRACTING_AUTHORITY,
        nif="000116019000085",
        wilaya_code="16",
        data_provenance=Organization.SourceType.SAMPLE_DATA
    )

@pytest.fixture
def second_contracting_org(db):
    """Second contracting authority (Wilaya d'Oran) for tenant isolation tests."""
    return Organization.objects.create(
        name="ولاية وهران - مديرية التعمير",
        org_type=Organization.OrgType.CONTRACTING_AUTHORITY,
        nif="000231019000042",
        wilaya_code="31",
        data_provenance=Organization.SourceType.SAMPLE_DATA
    )

@pytest.fixture
def economic_operator_org(db):
    """Sample economic operator company."""
    return Organization.objects.create(
        name="شركة الإنجازات الوطنية للأشغال الكبرى (SARL)",
        org_type=Organization.OrgType.ECONOMIC_OPERATOR,
        nif="001816001234567",
        registration_number="16/00-1234567B18",
        wilaya_code="16",
        data_provenance=Organization.SourceType.SAMPLE_DATA
    )

@pytest.fixture
def officer_user(db, contracting_org):
    """Contracting Authority Officer user."""
    return User.objects.create_user(
        email="officer@alger-marches.dz",
        password="ValidStrongPassword2026!",
        full_name="كريم بلقاسم",
        organization=contracting_org,
        role=User.Role.CONTRACTING_AUTHORITY_OFFICER
    )

@pytest.fixture
def other_officer_user(db, second_contracting_org):
    """Contracting Authority Officer in a different organization."""
    return User.objects.create_user(
        email="officer.oran@oran-marches.dz",
        password="ValidStrongPassword2026!",
        full_name="أحمد زبانا",
        organization=second_contracting_org,
        role=User.Role.CONTRACTING_AUTHORITY_OFFICER
    )

@pytest.fixture
def bidder_user(db, economic_operator_org):
    """Economic Operator representative user."""
    return User.objects.create_user(
        email="bidder@injazat-algerie.dz",
        password="ValidStrongPassword2026!",
        full_name="سمير بن علي",
        organization=economic_operator_org,
        role=User.Role.ECONOMIC_OPERATOR_USER
    )

@pytest.fixture
def sample_procurement(db, contracting_org, officer_user):
    """Draft procurement instance."""
    return Procurement.objects.create(
        procurement_number="2026/01/DEP",
        title="مشروع بناء مجمع مدرسي صنف ج - الجزائر",
        description="إنجاز مجمع مدرسي بكامل المرافق والتجهيزات",
        organization=contracting_org,
        estimated_budget=Decimal('150000000.00'),
        status=Procurement.Status.DRAFT,
        submission_deadline=timezone.now() + timezone.timedelta(days=30),
        created_by=officer_user,
        data_provenance=Procurement.SourceType.SAMPLE_DATA
    )

@pytest.fixture
def central_admin_org(db):
    """Central Administration Authority (Ministère / Commission Nationale des Marchés)."""
    return Organization.objects.create(
        name="اللجنة الوطنية للصفقات العمومية - وزارة المالية",
        org_type=Organization.OrgType.CENTRAL_ADMIN,
        nif="000000000000001",
        wilaya_code="16",
        data_provenance=Organization.SourceType.SAMPLE_DATA
    )

@pytest.fixture
def central_admin_user(db, central_admin_org):
    """Central Administration Supervisor user."""
    return User.objects.create_user(
        email="admin@marches-publics.dz",
        password="ValidStrongPassword2026!",
        full_name="مراقب الدولة للصفقات",
        organization=central_admin_org,
        role=User.Role.CENTRAL_ADMIN
    )

