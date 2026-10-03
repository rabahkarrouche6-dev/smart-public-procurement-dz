"""Document model enforcing private storage, malware inspection status, and SHA-256 hashes."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import TenantScopedModel

class Document(TenantScopedModel):
    """Secure private document entity with cryptographic integrity."""
    class SecurityStatus(models.TextChoices):
        PENDING_SCAN = 'PENDING_SCAN', _('قيد الفحص الأمني')
        CLEAN = 'CLEAN', _('سليم ومؤكد خلوه من البرمجيات الخبيثة')
        QUARANTINED = 'QUARANTINED', _('في الحجر الأمني (ملف مشبوه)')

    class Status(models.TextChoices):
        UPLOADED = 'UPLOADED', _('تم الرفع')
        PROCESSING = 'PROCESSING', _('قيد المعالجة والفحص')
        VERIFIED = 'VERIFIED', _('تم التحقق والتصديق')
        REQUIRES_REVIEW = 'REQUIRES_REVIEW', _('يتطلب مراجعة وتدقيقاً')
        REJECTED = 'REJECTED', _('مرفوض')

    title = models.CharField(
        max_length=255,
        verbose_name=_("عنوان أو وصف الوثيقة")
    )
    file_path = models.CharField(
        max_length=500,
        verbose_name=_("المسار التخزيني الآمن")
    )
    file_size_bytes = models.PositiveBigIntegerField(
        default=0,
        verbose_name=_("حجم الملف بالبايت")
    )
    mime_type = models.CharField(
        max_length=100,
        default='application/pdf',
        verbose_name=_("نوع الملف (MIME)")
    )
    file_hash_sha256 = models.CharField(
        max_length=64,
        db_index=True,
        verbose_name=_("البصمة الرقمية (SHA-256)")
    )
    security_status = models.CharField(
        max_length=20,
        choices=SecurityStatus.choices,
        default=SecurityStatus.PENDING_SCAN,
        verbose_name=_("الحالة الأمنية")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPLOADED,
        db_index=True,
        verbose_name=_("حالة تدقيق وتصديق الوثيقة")
    )
    is_private = models.BooleanField(
        default=True,
        verbose_name=_("ملف محمي (غير متاح للعامة)")
    )
    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("المستخدم الذي قام بالرفع")
    )

    class Meta:
        verbose_name = _("وثيقة رسمية")
        verbose_name_plural = _("الوثائق الرسمية")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} [{self.get_security_status_display()}] - {self.get_status_display()}"
