"""Legal text knowledge models with exact article citations and bilingual versions."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import BaseModel

class LegalDocument(BaseModel):
    """Authoritative Algerian legal document (Loi, Décret présidentiel, etc.)."""
    class LegalType(models.TextChoices):
        LAW = 'LAW', _('قانون (Loi)')
        PRESIDENTIAL_DECREE = 'PRESIDENTIAL_DECREE', _('مرسوم رئاسي')
        EXECUTIVE_DECREE = 'EXECUTIVE_DECREE', _('مرسوم تنفيذي')
        MINISTERIAL_ORDER = 'MINISTERIAL_ORDER', _('قرار وزاري')
        CIRCULAR = 'CIRCULAR', _('منشور وزاري')

    class Status(models.TextChoices):
        IN_FORCE = 'IN_FORCE', _('ساري المفعول')
        AMENDED = 'AMENDED', _('معدل جزئياً')
        ABROGATED = 'ABROGATED', _('ملغى')

    title = models.CharField(
        max_length=255,
        verbose_name=_("عنوان النص القانوني")
    )
    legal_type = models.CharField(
        max_length=30,
        choices=LegalType.choices,
        verbose_name=_("طبيعة النص")
    )
    official_number = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name=_("الرقم الرسمي (مثال: 23-12 أو 15-247)")
    )
    promulgation_date = models.DateField(
        verbose_name=_("تاريخ الإصدار")
    )
    joradp_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("مرجع الجريدة الرسمية (JORADP)")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_FORCE,
        verbose_name=_("حالة السريان")
    )

    class Meta:
        verbose_name = _("نص قانوني رسمي")
        verbose_name_plural = _("النصوص القانونية الرسمية")
        ordering = ['-promulgation_date']

    def __str__(self):
        return f"{self.get_legal_type_display()} رقم {self.official_number}: {self.title}"

class LegalArticle(BaseModel):
    """Individual article chunk from an authoritative legal text."""
    document = models.ForeignKey(
        LegalDocument,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name=_("النص القانوني المصدر")
    )
    article_number = models.CharField(
        max_length=30,
        db_index=True,
        verbose_name=_("رقم المادة")
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("عنوان أو موضوع المادة")
    )
    content_ar = models.TextField(
        verbose_name=_("نص المادة باللغة العربية (النص الرسمي)")
    )
    content_fr = models.TextField(
        blank=True,
        verbose_name=_("نص المادة باللغة الفرنسية")
    )
    keywords = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("الكلمات المفتاحية والتصنيفات")
    )

    class Meta:
        verbose_name = _("مادة قانونية")
        verbose_name_plural = _("المواد القانونية")
        unique_together = ('document', 'article_number')
        ordering = ['document', 'article_number']

    def __str__(self):
        return f"المادة {self.article_number} من {self.document.official_number}"
