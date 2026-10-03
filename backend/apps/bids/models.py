"""Bid submission and fold management models."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import BaseModel

class Bid(BaseModel):
    """
    Bid submitted by an Economic Operator for a public procurement tender.
    Folds remain sealed and tamper-locked until official opening session.
    """
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('مسودة قيد التحضير')
        SUBMITTED = 'SUBMITTED', _('تم الإيداع رسمياً (مغلق ومشفر)')
        LOCKED = 'LOCKED', _('مغلق قانونياً بعد انقضاء الأجل')
        OPENED = 'OPENED', _('تم فتح الظرف في الجلسة العلنية')
        UNDER_EVALUATION = 'UNDER_EVALUATION', _('قيد دراسة وتقييم العروض')
        ACCEPTED = 'ACCEPTED', _('مقبول ومطابق')
        REJECTED = 'REJECTED', _('مرفوض وغير مطابق')
        WITHDRAWN = 'WITHDRAWN', _('مسحوب من طرف العارض')

    procurement = models.ForeignKey(
        'procurements.Procurement',
        on_delete=models.PROTECT,
        related_name='bids',
        verbose_name=_("الصفقة العمومية المعنية")
    )
    bidder = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.PROTECT,
        related_name='submitted_bids',
        verbose_name=_("المتعامل الاقتصادي العارض")
    )
    submitted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='user_bids',
        verbose_name=_("المستخدم المودع للعرض")
    )
    status = models.CharField(
        max_length=25,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name=_("حالة العرض")
    )
    # Financial proposal
    financial_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name=_("المبلغ المالي المقترح (دج)")
    )
    execution_delay_days = models.PositiveIntegerField(
        default=30,
        verbose_name=_("أجل التنفيذ المقترح (بالأيام)")
    )
    # Confidential sealed document attachments
    technical_offer_doc = models.ForeignKey(
        'documents.Document',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tech_bids',
        verbose_name=_("ملف العرض التقني")
    )
    financial_offer_doc = models.ForeignKey(
        'documents.Document',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='financial_bids',
        verbose_name=_("ملف العرض المالي")
    )
    administrative_doc = models.ForeignKey(
        'documents.Document',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_bids',
        verbose_name=_("ملف الترشح والوثائق الإدارية")
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ وساعة الإيداع المؤكد")
    )
    is_opened = models.BooleanField(
        default=False,
        verbose_name=_("تم فتح الأظرفة")
    )
    opening_timestamp = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("توقيت فتح الأظرفة")
    )
    # Deterministic evaluation scores (calculated by Evaluation Formula Engine)
    technical_score = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("العلامة التقنية الممنوحة")
    )
    financial_score = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("العلامة المالية الممنوحة")
    )
    total_score = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("العلامة الإجمالية المرجحة")
    )
    ranking = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("الترتيب النهائي")
    )

    class Meta:
        verbose_name = _("عرض متعهد")
        verbose_name_plural = _("عروض المتعهدين")
        unique_together = ('procurement', 'bidder')
        ordering = ['ranking', '-total_score', 'financial_amount']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(financial_amount__gte=0),
                name='positive_bid_financial_amount'
            )
        ]

    def __str__(self):
        return f"Bid by {self.bidder.name} for {self.procurement.procurement_number} [{self.get_status_display()}]"
