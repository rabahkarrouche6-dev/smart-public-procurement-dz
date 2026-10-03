"""Tender document entity (Cahier des charges / DAO) with immutable versioning."""
from django.db import models
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from apps.common.models import TenantScopedModel

class TenderDocument(TenantScopedModel):
    """
    Tender Document (دفتر الشروط / ملف استشارة) governing a procurement.
    Once marked is_published=True, modifications are locked and require a new version.
    """
    procurement = models.ForeignKey(
        'procurements.Procurement',
        on_delete=models.PROTECT,
        related_name='tender_documents',
        verbose_name=_("الصفقة العمومية المرتبطة")
    )
    version = models.PositiveIntegerField(
        default=1,
        verbose_name=_("رقم الإصدار (Version)")
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("عنوان دفتر الشروط")
    )
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.PROTECT,
        related_name='tender_docs',
        verbose_name=_("الملف المرفق الأصلي")
    )
    is_published = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("منشور رسمياً للتحميل")
    )
    content_hash = models.CharField(
        max_length=64,
        blank=True,
        verbose_name=_("البصمة الرقمية للنسخة")
    )
    # Extracted structured criteria for deterministic scoring
    extracted_criteria = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("معايير التقييم المستخرجة")
    )
    # Administrative & technical eligibility conditions
    eligibility_conditions = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("شروط التأهيل والقدرات الدنيا")
    )

    class Meta:
        verbose_name = _("دفتر شروط")
        verbose_name_plural = _("دفاتر الشروط")
        unique_together = ('procurement', 'version')
        ordering = ['procurement', '-version']

    def __str__(self):
        return f"DAO v{self.version} - {self.procurement.procurement_number}"

    def save(self, *args, **kwargs):
        # Protect published tender documents from modification
        if self.pk:
            prev = TenderDocument.objects.filter(pk=self.pk).first()
            if prev and prev.is_published and not kwargs.get('force_update', False):
                # Only allows creating a higher version
                raise PermissionDenied(_("لا يمكن تعديل دفتر شروط تم نشره رسمياً. يرجى إصدار ملحق أو نسخة جديدة v+1."))
        super().save(*args, **kwargs)
