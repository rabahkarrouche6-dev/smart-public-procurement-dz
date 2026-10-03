"""Serializers and views for Deterministic Evaluation."""
from decimal import Decimal
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.evaluations.models import EvaluationFormula, EvaluationCriterion, BidEvaluationRecord
from apps.evaluations.services.deterministic_engine import evaluate_bids_for_procurement
from apps.bids.models import Bid

class EvaluationCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationCriterion
        fields = ['id', 'code', 'label', 'max_points']

class EvaluationFormulaSerializer(serializers.ModelSerializer):
    criteria = EvaluationCriterionSerializer(many=True, read_only=True)

    class Meta:
        model = EvaluationFormula
        fields = [
            'id', 'procurement', 'version', 'is_official',
            'technical_weight_percent', 'financial_weight_percent',
            'minimum_technical_threshold', 'decimal_precision', 'criteria'
        ]

class BidEvaluationRecordSerializer(serializers.ModelSerializer):
    bidder_name = serializers.CharField(source='bid.bidder.name', read_only=True)

    class Meta:
        model = BidEvaluationRecord
        fields = [
            'id', 'bid', 'bidder_name', 'formula', 'is_simulation',
            'criteria_scores', 'raw_technical_score', 'normalized_financial_score',
            'final_weighted_score', 'calculation_steps', 'evaluated_by', 'created_at'
        ]

class CalculateEvaluationSerializer(serializers.Serializer):
    formula_id = serializers.UUIDField()
    criteria_inputs = serializers.DictField(child=serializers.DictField())
    is_simulation = serializers.BooleanField(default=False)

class EvaluationViewSet(viewsets.ModelViewSet):
    """Evaluation formulas and deterministic calculation execution."""
    queryset = EvaluationFormula.objects.all()
    serializer_class = EvaluationFormulaSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='calculate')
    def execute_evaluation(self, request):
        serializer = CalculateEvaluationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        formula_id = serializer.validated_data['formula_id']
        raw_inputs = serializer.validated_data['criteria_inputs']
        is_simulation = serializer.validated_data['is_simulation']

        formula = EvaluationFormula.objects.prefetch_related('criteria').get(id=formula_id)
        bids = list(Bid.objects.filter(procurement=formula.procurement, status__in=[
            Bid.Status.OPENED, Bid.Status.UNDER_EVALUATION, Bid.Status.ACCEPTED
        ]))

        if not bids:
            return Response(
                {'error': 'لا توجد أظرفة مفتوحة مؤهلة للتقييم في هذه الصفقة.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Convert numeric inputs to Decimal
        criteria_inputs = {}
        for bid_id, crit_dict in raw_inputs.items():
            criteria_inputs[str(bid_id)] = {
                code: Decimal(str(val)) for code, val in crit_dict.items()
            }

        records = evaluate_bids_for_procurement(
            formula=formula,
            bids=bids,
            criteria_inputs=criteria_inputs,
            evaluator_user=request.user,
            is_simulation=is_simulation,
            request=request
        )

        return Response({
            'is_simulation': is_simulation,
            'results': BidEvaluationRecordSerializer(records, many=True).data
        }, status=status.HTTP_200_OK)
