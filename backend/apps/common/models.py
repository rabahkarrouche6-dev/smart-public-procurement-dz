"""Core base models enforcing timestamps, UUID primary keys, and tenant scoping."""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class BaseModel(models.Model):
    """Abstract base model with immutable UUID and timezone-aware timestamps."""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name=_("تاريخ الإنشاء")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("تاريخ التحديث")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("نشط")
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

class ProvenanceModel(models.Model):
    """Model tracking provenance classification (Real, Official, Sample, etc.)."""
    class SourceType(models.TextChoices):
        OFFICIAL_SOURCE = 'OFFICIAL_SOURCE', _('مصدر رسمي معتمد')
        API_RETRIEVED = 'API_RETRIEVED', _('مسترجع عبر واجهة برمجة مؤكدة')
        USER_PROVIDED = 'USER_PROVIDED', _('مقدم من المستخدم')
        AI_GENERATED = 'AI_GENERATED', _('مولد بمساعدة الذكاء الاصطناعي')
        SAMPLE_DATA = 'SAMPLE_DATA', _('بيانات تجريبية توضيحية')

    data_provenance = models.CharField(
        max_length=30,
        choices=SourceType.choices,
        default=SourceType.USER_PROVIDED,
        verbose_name=_("مصدر ومصداقية البيانات")
    )

    class Meta:
        abstract = True

class TenantScopedModel(BaseModel, ProvenanceModel):
    """Abstract model enforcing explicit multi-tenancy and organization isolation."""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_items",
        db_index=True,
        verbose_name=_("الهيئة أو المؤسسة المالكة")
    )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['organization', 'created_at']),
        ]
