"""Tamper-resistant audit log model for all consequential platform operations."""
import uuid
from django.db import models
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

class AuditLog(models.Model):
    """
    Append-only audit record capturing security, workflow, and data transitions.
    Modifications and deletions are explicitly prevented at model level.
    """
    class ResultStatus(models.TextChoices):
        SUCCESS = 'SUCCESS', _('ناجحة')
        FAILURE = 'FAILURE', _('فاشلة')
        DENIED = 'DENIED', _('مرفوضة الصلاحية')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    actor = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_actions',
        verbose_name=_("المستخدم المنفذ")
    )
    actor_email = models.EmailField(
        blank=True,
        verbose_name=_("بريد المنفذ")
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name=_("الهيئة المعنية")
    )
    action = models.CharField(
        max_length=60,
        db_index=True,
        verbose_name=_("نوع الإجراء")
    )
    resource_type = models.CharField(
        max_length=60,
        db_index=True,
        verbose_name=_("نوع الكيان")
    )
    resource_id = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name=_("معرف الكيان")
    )
    old_values = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_("القيم السابقة")
    )
    new_values = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_("القيم الجديدة")
    )
    correlation_id = models.CharField(
        max_length=100,
        db_index=True,
        blank=True,
        verbose_name=_("معرف الارتباط (Correlation ID)")
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("عنوان IP")
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name=_("وكيل المتصفح")
    )
    result = models.CharField(
        max_length=20,
        choices=ResultStatus.choices,
        default=ResultStatus.SUCCESS,
        db_index=True,
        verbose_name=_("النتيجة")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name=_("وقت التسجيل")
    )

    class Meta:
        verbose_name = _("سجل تدقيق")
        verbose_name_plural = _("سجلات التدقيق والمطابقة")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['action', 'created_at']),
        ]

    def __str__(self):
        return f"[{self.created_at}] {self.action} on {self.resource_type}:{self.resource_id} by {self.actor_email}"

    def save(self, *args, **kwargs):
        # Prevent updates to existing audit entries (Append-only guarantee)
        if self.pk and AuditLog.objects.filter(pk=self.pk).exists():
            raise PermissionDenied(_("سجلات التدقيق غير قابلة للتعديل أو التحوير."))
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Prevent deletion of audit entries
        raise PermissionDenied(_("سجلات التدقيق غير قابلة للحذف."))
