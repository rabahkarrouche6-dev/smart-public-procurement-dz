"""
Deterministic Mathematical Evaluation Engine.
Conforming strictly to Skill 09: Pure Decimal arithmetic, zero LLM dependency,
verifiable rounding, and step-by-step audit trail.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.evaluations.models import EvaluationFormula, BidEvaluationRecord
from apps.bids.models import Bid
from apps.audit.services import record_audit_event

ENGINE_VERSION = "1.0.0-DZ-DETERMINISTIC"

def evaluate_bids_for_procurement(
    formula: EvaluationFormula,
    bids: List[Bid],
    criteria_inputs: Dict[str, Dict[str, Decimal]],
    evaluator_user=None,
    is_simulation: bool = False,
    request=None
) -> List[BidEvaluationRecord]:
    """
    Evaluates a set of opened bids deterministically using Decimal precision.
    
    formula: The EvaluationFormula instance defining weights and criteria.
    bids: List of Bid instances to rank.
    criteria_inputs: { bid_id_str: { criterion_code: Decimal(score) } }
    is_simulation: If True, produces audit records without overwriting official bid ranks.
    """
    # 1. Validate weights integrity (must sum to exactly 100.00%)
    total_weight = formula.technical_weight_percent + formula.financial_weight_percent
    if total_weight != Decimal('100.00'):
        raise ValidationError(f"مجموع نسب الترجيح يجب أن يساوي 100% تماماً. المجموع الحالي: {total_weight}%")

    if not bids:
        return []

    # 2. Extract valid active criteria
    criteria_map = {c.code: c for c in formula.criteria.all()}
    precision = formula.decimal_precision
    quantize_pattern = Decimal('1.' + '0' * precision)

    # 3. Identify minimum financial proposal for the group (P_min)
    valid_bids = [b for b in bids if b.financial_amount > Decimal('0')]
    if not valid_bids:
        raise ValidationError("لا توجد مبالغ مالية صالحة لحساب المعادلة المالية.")

    min_price = min(b.financial_amount for b in valid_bids)

    evaluation_records = []
    calculated_bids_data = []

    # 4. Deterministic score calculation per bid
    for bid in bids:
        steps = []
        steps.append(f"محدد المحرك: {ENGINE_VERSION}")
        steps.append(f"المبلغ المالي للعرض: {bid.financial_amount} دج (أقل مبلغ للمجموعة: {min_price} دج)")

        # Technical Score Summation
        bid_criteria = criteria_inputs.get(str(bid.id), {})
        raw_tech_score = Decimal('0.0000')

        for code, criterion in criteria_map.items():
            assigned_points = Decimal(str(bid_criteria.get(code, '0.00')))
            if assigned_points < Decimal('0') or assigned_points > criterion.max_points:
                raise ValidationError(
                    f"علامة المعيار '{criterion.label}' يجب أن تكون بين 0 و {criterion.max_points}."
                )
            raw_tech_score += assigned_points
            steps.append(f"معيار [{code}] ({criterion.label}): {assigned_points} / {criterion.max_points}")

        steps.append(f"العلامة التقنية الإجمالية الخام: {raw_tech_score}")

        # Financial Score Calculation: (P_min / P_bid) * 100
        if bid.financial_amount > Decimal('0'):
            fin_ratio = (min_price / bid.financial_amount) * Decimal('100.0000')
            normalized_fin_score = fin_ratio.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
            steps.append(f"المعادلة المالية: ({min_price} / {bid.financial_amount}) * 100 = {normalized_fin_score}")
        else:
            normalized_fin_score = Decimal('0.0000')
            steps.append("المعادلة المالية: 0 (مبلغ غير صالح)")

        # Final Weighted Formula
        # Final = (Tech * W_tech / 100) + (Fin * W_fin / 100)
        weighted_tech = (raw_tech_score * formula.technical_weight_percent) / Decimal('100')
        weighted_fin = (normalized_fin_score * formula.financial_weight_percent) / Decimal('100')
        total_score = (weighted_tech + weighted_fin).quantize(quantize_pattern, rounding=ROUND_HALF_UP)

        steps.append(
            f"الترجيح النهائي: ({raw_tech_score} * {formula.technical_weight_percent}%) + "
            f"({normalized_fin_score} * {formula.financial_weight_percent}%) = {total_score}"
        )

        calculated_bids_data.append({
            'bid': bid,
            'raw_tech': raw_tech_score,
            'norm_fin': normalized_fin_score,
            'total': total_score,
            'steps': steps,
            'criteria': bid_criteria,
        })

    # 5. Rank sorting: descending total score, then lowest price as tie-breaker
    calculated_bids_data.sort(key=lambda x: (-x['total'], x['bid'].financial_amount))

    # 6. Persistence & Audit
    with transaction.atomic():
        for rank, item in enumerate(calculated_bids_data, start=1):
            item['steps'].append(f"الترتيب النهائي المحسوب: المرتبة {rank}")

            serialized_criteria = {k: str(v) for k, v in item['criteria'].items()}
            record = BidEvaluationRecord.objects.create(
                bid=item['bid'],
                formula=formula,
                is_simulation=is_simulation,
                criteria_scores=serialized_criteria,
                raw_technical_score=item['raw_tech'],
                normalized_financial_score=item['norm_fin'],
                final_weighted_score=item['total'],
                calculation_steps=item['steps'],
                evaluated_by=evaluator_user
            )
            evaluation_records.append(record)

            if not is_simulation:
                # Update official bid scores and status
                item['bid'].technical_score = item['raw_tech']
                item['bid'].financial_score = item['norm_fin']
                item['bid'].total_score = item['total']
                item['bid'].ranking = rank
                item['bid'].status = Bid.Status.UNDER_EVALUATION
                item['bid'].save(update_fields=['technical_score', 'financial_score', 'total_score', 'ranking', 'status', 'updated_at'])

        record_audit_event(
            action='DETERMINISTIC_EVALUATION_COMPLETED',
            resource_type='Procurement',
            resource_id=str(formula.procurement.id),
            actor=evaluator_user,
            organization=formula.procurement.organization,
            new_values={
                'formula_version': formula.version,
                'is_simulation': is_simulation,
                'bids_evaluated_count': len(evaluation_records)
            },
            request=request
        )

    return evaluation_records
