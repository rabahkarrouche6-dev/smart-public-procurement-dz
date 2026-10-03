"""Evaluation models and deterministic calculation tracking."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import TenantScopedModel, BaseModel

class EvaluationFormula(TenantScopedModel):
    """
    Deterministic scoring formula configuration for a procurement tender.
    Formula configuration is locked once official evaluations are completed.
    """
    procurement = models.ForeignKey(
        'procurements.Procurement',
        on_delete=models.PROTECT,
        related_name='evaluation_formulas',
        verbose_name=_("الصفقة العمومية")
    )
    version = models.PositiveIntegerField(
        default=1,
        verbose_name=_("إصدار صيغة التقييم")
    )
    is_official = models.BooleanField(
        default=True,
        verbose_name=_("صيغة رسمية معتمدة")
    )
    technical_weight_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=70.00,
        verbose_name=_("نسبة ترجيح العرض التقني (%)")
    )
    financial_weight_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=30.00,
        verbose_name=_("نسبة ترجيح العرض المالي (%)")
    )
    minimum_technical_threshold = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=50.00,
        verbose_name=_("العتبة الدنيا للإقصاء التقني (من 100)")
    )
    decimal_precision = models.PositiveSmallIntegerField(
        default=2,
        verbose_name=_("عدد الخانات العشرية للتقريب")
    )

    class Meta:
        verbose_name = _("صيغة تقييم العروض")
        verbose_name_plural = _("صيغ تقييم العروض")
        unique_together = ('procurement', 'version')

    def __str__(self):
        return f"Formula v{self.version} for {self.procurement.procurement_number} ({self.technical_weight_percent}% Tech / {self.financial_weight_percent}% Fin)"

class EvaluationCriterion(BaseModel):
    """Specific technical scoring criterion."""
    formula = models.ForeignKey(
        EvaluationFormula,
        on_delete=models.CASCADE,
        related_name='criteria',
        verbose_name=_("صيغة التقييم")
    )
    code = models.CharField(
        max_length=30,
        verbose_name=_("رمز المعيار")
    )
    label = models.CharField(
        max_length=200,
        verbose_name=_("نص أو مسمى المعيار")
    )
    max_points = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name=_("العلامة القصوى للنقاط")
    )

    class Meta:
        unique_together = ('formula', 'code')
        ordering = ['code']

    def __str__(self):
        return f"[{self.code}] {self.label} (Max: {self.max_points})"

from django.core.serializers.json import DjangoJSONEncoder

class BidEvaluationRecord(BaseModel):
    """Immutable calculation result produced by the Deterministic Formula Engine."""
    bid = models.ForeignKey(
        'bids.Bid',
        on_delete=models.PROTECT,
        related_name='evaluation_records',
        verbose_name=_("العرض المعني")
    )
    formula = models.ForeignKey(
        EvaluationFormula,
        on_delete=models.PROTECT,
        verbose_name=_("صيغة التقييم المعتمدة")
    )
    is_simulation = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("محاكاة تجريبية (ليست رسمية)")
    )
    criteria_scores = models.JSONField(
        default=dict,
        encoder=DjangoJSONEncoder,
        verbose_name=_("تفاصيل نقاط المعايير التقنية")
    )
    raw_technical_score = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        verbose_name=_("العلامة التقنية الخام")
    )
    normalized_financial_score = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        verbose_name=_("العلامة المالية المطبقة")
    )
    final_weighted_score = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        verbose_name=_("العلامة النهائية المرجحة")
    )
    calculation_steps = models.JSONField(
        default=list,
        verbose_name=_("خطوات العمليات الحسابية التفصيلية")
    )
    evaluated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("المقيم المسؤول")
    )

    class Meta:
        verbose_name = _("محضر تقييم حسابي")
        verbose_name_plural = _("محاضر التقييم الحسابية")
        ordering = ['-final_weighted_score']
