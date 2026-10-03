"""Provisional and Final Acceptance PV models."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import TenantScopedModel

class ReceptionRecord(TenantScopedModel):
    """Reception PV (محضر استلام - Procès-Verbal de Réception)."""
    class ReceptionType(models.TextChoices):
        PROVISIONAL = 'PROVISIONAL', _('استلام مؤقت (Réception Provisoire)')
        FINAL = 'FINAL', _('استلام نهائي (Réception Définitive)')

    class Decision(models.TextChoices):
        ACCEPTED_WITHOUT_RESERVATIONS = 'ACCEPTED_WITHOUT_RESERVATIONS', _('قبول بدون تحفظات')
        ACCEPTED_WITH_RESERVATIONS = 'ACCEPTED_WITH_RESERVATIONS', _('قبول مع إبداء تحفظات')
        REJECTED = 'REJECTED', _('رفض الاستلام لعدم المطابقة')

    class Status(models.TextChoices):
        PLANNED = 'PLANNED', _('مخطط ومبرمج')
        PARTIAL = 'PARTIAL', _('استلام جزئي')
        FINAL = 'FINAL', _('استلام نهائي')
        REJECTED = 'REJECTED', _('مرفوض')

    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.PROTECT,
        related_name='receptions',
        verbose_name=_("العقد المعني")
    )
    reception_type = models.CharField(
        max_length=20,
        choices=ReceptionType.choices,
        verbose_name=_("نوع الاستلام")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
        db_index=True,
        verbose_name=_("حالة الاستلام")
    )
    pv_number = models.CharField(
        max_length=50,
        verbose_name=_("رقم محضر الاستلام")
    )
    reception_date = models.DateField(
        verbose_name=_("تاريخ الاستلام")
    )
    decision = models.CharField(
        max_length=35,
        choices=Decision.choices,
        verbose_name=_("قرار لجنة الاستلام")
    )
    reservations_text = models.TextField(
        blank=True,
        verbose_name=_("قائمة التحفظات والملاحظات")
    )
    guarantee_release_approved = models.BooleanField(
        default=False,
        verbose_name=_("الموافقة على رفع اليد عن كفالة الضمان")
    )

    class Meta:
        verbose_name = _("محضر استلام")
        verbose_name_plural = _("محاضر الاستلام")
        ordering = ['-reception_date']

    def __str__(self):
        return f"PV {self.pv_number} ({self.get_reception_type_display()}) - {self.contract.contract_number}"
