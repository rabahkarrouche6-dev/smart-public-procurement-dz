"""Procurement model representing public tenders and their FSM lifecycle."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import TenantScopedModel

class Procurement(TenantScopedModel):
    """
    Public Procurement (الصفقة العمومية) conforming to Algerian Public Procurement Law (Loi 23-12 / Décret 15-247).
    """
    class ProcedureType(models.TextChoices):
        OPEN_TENDER = 'OPEN_TENDER', _('طلب عروض مفتوح')
        RESTRICTED_TENDER = 'RESTRICTED_TENDER', _('طلب عروض محدود')
        COMPETITIVE_DIALOGUE = 'COMPETITIVE_DIALOGUE', _('مسابقة أو حوار تنافسي')
        CONSULTATION = 'CONSULTATION', _('استشارة / إجراء مكيف')

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('مسودة')
        PREPARATION = 'PREPARATION', _('قيد التحضير والإعداد')
        APPROVAL = 'APPROVAL', _('مصادقة لجنة الصفقات')
        PUBLICATION = 'PUBLICATION', _('إشهار ونشر الإعلان')
        BID_SUBMISSION = 'BID_SUBMISSION', _('مرحلة إيداع العروض')
        OPENING = 'OPENING', _('جلسة فتح الأظرفة')
        EVALUATION = 'EVALUATION', _('تقييم العروض والترتيب')
        PROVISIONAL_AWARD = 'PROVISIONAL_AWARD', _('الإعلان عن المنح المؤقت')
        APPEAL = 'APPEAL', _('فترة الطعون القانونية')
        CONTRACT = 'CONTRACT', _('إبرام وتوقيع العقد')
        EXECUTION = 'EXECUTION', _('مرحلة التنفيذ الميداني')
        RECEPTION = 'RECEPTION', _('الاستلام المؤقت / النهائي')
        CLOSED = 'CLOSED', _('مغلقة ومنتهية')
        CANCELLED = 'CANCELLED', _('ملغاة')

    procurement_number = models.CharField(
        max_length=60,
        db_index=True,
        verbose_name=_("رقم الصفقة الرسمي")
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("موضوع الصفقة العمومية")
    )
    description = models.TextField(
        verbose_name=_("تفاصيل ومواصفات الصفقة")
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='procurements',
        verbose_name=_("المشروع المرتبط")
    )
    procedure_type = models.CharField(
        max_length=30,
        choices=ProcedureType.choices,
        default=ProcedureType.OPEN_TENDER,
        verbose_name=_("طريقة وإجراء الإبرام")
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name=_("حالة الصفقة الحالية")
    )
    estimated_budget = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name=_("التقدير الإداري المالي (دج)")
    )
    currency = models.CharField(
        max_length=10,
        default='DZD',
        verbose_name=_("العملة")
    )
    publication_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ نشر الإعلان")
    )
    submission_deadline = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("الأجل الأقصى لإيداع العروض")
    )
    opening_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ جلسة فتح الأظرفة")
    )
    evaluation_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ جلسة تقييم العروض")
    )
    bid_validity_days = models.PositiveIntegerField(
        default=90,
        verbose_name=_("مدة صلاحية العروض (بالأيام)")
    )
    appeal_deadline = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("آخر أجل لتقديم الطعون")
    )
    legal_source_reference = models.CharField(
        max_length=200,
        default='Loi 23-12 relative aux marchés publics / Décret présidentiel 15-247',
        verbose_name=_("المرجعية القانونية المطبقة")
    )
    requires_tender_fee = models.BooleanField(
        default=False,
        verbose_name=_("سحب دفتر الشروط بمقابل مالي")
    )
    tender_fee_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("مبلغ حقوق سحب دفتر الشروط (دج)")
    )
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_procurements',
        verbose_name=_("المستخدم المنشئ")
    )

    class Meta:
        verbose_name = _("صفقة عمومية")
        verbose_name_plural = _("الصفقات العمومية")
        unique_together = ('organization', 'procurement_number')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status', 'created_at']),
            models.Index(fields=['status', 'submission_deadline']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(estimated_budget__gte=0) & models.Q(tender_fee_amount__gte=0),
                name='positive_procurement_financials'
            )
        ]

    def __str__(self):
        return f"{self.procurement_number}: {self.title} ({self.get_status_display()})"
