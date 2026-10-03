"""Notification models for multi-channel event messaging."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import BaseModel

class Notification(BaseModel):
    """System notification dispatched to users or organizations."""
    class NotificationType(models.TextChoices):
        DEADLINE_ALERT = 'DEADLINE_ALERT', _('تنبيه اقتراب أجل قانوني')
        PROCUREMENT_PUBLISHED = 'PROCUREMENT_PUBLISHED', _('نشر إعلان صفقة جديدة')
        BID_SUBMITTED = 'BID_SUBMITTED', _('تأكيد إيداع العرض')
        BID_OPENED = 'BID_OPENED', _('فتح الأظرفة')
        EVALUATION_COMPLETED = 'EVALUATION_COMPLETED', _('استكمال تقييم العروض')
        PROVISIONAL_AWARD = 'PROVISIONAL_AWARD', _('إعلان المنح المؤقت للصفقة')
        RISK_ALERT = 'RISK_ALERT', _('إنذار بمؤشر مخاطر')

    recipient = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_("المستلم")
    )
    notification_type = models.CharField(
        max_length=35,
        choices=NotificationType.choices,
        verbose_name=_("نوع التنبيه")
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("عنوان التنبيه")
    )
    message = models.TextField(
        verbose_name=_("نص الرسالة والتفاصيل")
    )
    resource_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("نوع الكيان المرتبط")
    )
    resource_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("معرف الكيان")
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("تمت القراءة")
    )

    class Meta:
        verbose_name = _("إشعار وتنبيه")
        verbose_name_plural = _("الإشعارات والتنبيهات")
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.title} -> {self.recipient.email}"
