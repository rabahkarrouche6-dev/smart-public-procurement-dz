"""Tests for Deterministic Evaluation Formula Engine (Skill 09)."""
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from apps.evaluations.models import EvaluationFormula, EvaluationCriterion
from apps.evaluations.services.deterministic_engine import evaluate_bids_for_procurement
from apps.bids.models import Bid
from apps.organizations.models import Organization

@pytest.mark.django_db
def test_deterministic_scoring_and_ranking(sample_procurement, contracting_org, officer_user, bidder_user):
    # Setup Formula: 70% Tech, 30% Fin
    formula = EvaluationFormula.objects.create(
        procurement=sample_procurement,
        organization=contracting_org,
        version=1,
        technical_weight_percent=Decimal('70.00'),
        financial_weight_percent=Decimal('30.00'),
        decimal_precision=2
    )
    crit1 = EvaluationCriterion.objects.create(formula=formula, code="TECH_EXPERIENCE", label="الخبرة المهنية", max_points=Decimal('50.00'))
    crit2 = EvaluationCriterion.objects.create(formula=formula, code="TECH_METHODOLOGY", label="منهجية التنفيذ", max_points=Decimal('50.00'))

    # Second bidder
    second_bidder_org = Organization.objects.create(
        name="مؤسسة البناء الحديث (EURL)",
        org_type=Organization.OrgType.ECONOMIC_OPERATOR,
        nif="001916007777777"
    )

    # Bid A: 10,000,000 DZD, Raw Tech: 40 + 40 = 80
    bid_a = Bid.objects.create(
        procurement=sample_procurement,
        bidder=bidder_user.organization,
        submitted_by=bidder_user,
        financial_amount=Decimal('10000000.00'),
        status=Bid.Status.OPENED
    )

    # Bid B: 12,000,000 DZD, Raw Tech: 45 + 45 = 90
    bid_b = Bid.objects.create(
        procurement=sample_procurement,
        bidder=second_bidder_org,
        submitted_by=bidder_user,
        financial_amount=Decimal('12000000.00'),
        status=Bid.Status.OPENED
    )

    criteria_inputs = {
        str(bid_a.id): {"TECH_EXPERIENCE": Decimal('40.00'), "TECH_METHODOLOGY": Decimal('40.00')},
        str(bid_b.id): {"TECH_EXPERIENCE": Decimal('45.00'), "TECH_METHODOLOGY": Decimal('45.00')}
    }

    records = evaluate_bids_for_procurement(
        formula=formula,
        bids=[bid_a, bid_b],
        criteria_inputs=criteria_inputs,
        evaluator_user=officer_user,
        is_simulation=False
    )

    assert len(records) == 2

    # Reload bids from database
    bid_a.refresh_from_db()
    bid_b.refresh_from_db()

    # Calculation checks:
    # Bid A: (80 * 0.70) + (100 * 0.30) = 56.00 + 30.00 = 86.00
    # Bid B: (90 * 0.70) + ((10M/12M)*100 * 0.30) = 63.00 + (83.3333 * 0.30) = 63.00 + 25.00 = 88.00
    assert bid_b.total_score == Decimal('88.00')
    assert bid_a.total_score == Decimal('86.00')
    assert bid_b.ranking == 1
    assert bid_a.ranking == 2

@pytest.mark.django_db
def test_formula_weights_validation_failure(sample_procurement, contracting_org):
    # Sum != 100.00%
    formula = EvaluationFormula.objects.create(
        procurement=sample_procurement,
        organization=contracting_org,
        version=1,
        technical_weight_percent=Decimal('50.00'),
        financial_weight_percent=Decimal('40.00')
    )
    with pytest.raises(ValidationError):
        evaluate_bids_for_procurement(
            formula=formula,
            bids=[],
            criteria_inputs={}
        )
