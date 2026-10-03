"""Contract models representing finalized procurement agreements."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import TenantScopedModel

class Contract(TenantScopedModel):
    """
    Finalized public procurement contract signed between Contracting Authority and winning Bidder.
    """
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('مسودة العقد')
        SIGNED = 'SIGNED', _('موقع ومصادق عليه')
        ACTIVE = 'ACTIVE', _('ساري المفعول قيد التنفيذ')
        COMPLETED = 'COMPLETED', _('مكتمل ومنتهي')
        TERMINATED = 'TERMINATED', _('مفسوخ')

    contract_number = models.CharField(
        max_length=60,
        unique=True,
        db_index=True,
        verbose_name=_("رقم العقد أو الصفقة المبرمة")
    )
    procurement = models.OneToOneField(
        'procurements.Procurement',
        on_delete=models.PROTECT,
        related_name='contract',
        verbose_name=_("الصفقة العمومية الأصلية")
    )
    winning_bid = models.OneToOneField(
        'bids.Bid',
        on_delete=models.PROTECT,
        related_name='awarded_contract',
        verbose_name=_("العرض الفائز المعتمد")
    )
    contractor = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.PROTECT,
        related_name='awarded_contracts',
        verbose_name=_("المتعامل الاقتصادي الحائز على الصفقة")
    )
    contract_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name=_("المبلغ الإجمالي للصفقة (دج)")
    )
    performance_guarantee_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name=_("مبلغ كفالة حسن التنفيذ (دج)")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name=_("حالة العقد")
    )
    signature_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ توقيع الصفقة")
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ سريان العقد")
    )
    completion_delay_months = models.PositiveIntegerField(
        default=6,
        verbose_name=_("مدة الإنجاز بالشهور")
    )

    class Meta:
        verbose_name = _("عقد صفقة عمومية")
        verbose_name_plural = _("عقود الصفقات العمومية")
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(contract_amount__gte=0) & models.Q(performance_guarantee_amount__gte=0),
                name='positive_contract_amounts'
            )
        ]

    def __str__(self):
        return f"Contract {self.contract_number} - {self.contractor.name} ({self.contract_amount} DZD)"


class ContractMilestone(TenantScopedModel):
    """Milestone associated with a public procurement contract."""
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('معلق')
        IN_PROGRESS = 'IN_PROGRESS', _('قيد الإنجاز')
        COMPLETED = 'COMPLETED', _('مكتمل ومستلم')
        DELAYED = 'DELAYED', _('متأخر')

    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='milestones',
        verbose_name=_("العقد المرتبط")
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("عنوان المرحلة التعاقدية")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("تفاصيل ومخرجات المرحلة")
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الاستحقاق")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("حالة المرحلة")
    )
    weight_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("نسبة الوزن الإجمالي (%)")
    )

    class Meta:
        verbose_name = _("مرحلة تعاقدية")
        verbose_name_plural = _("المراحل التعاقدية")
        ordering = ['due_date', 'created_at']

    def __str__(self):
        return f"{self.title} - {self.contract.contract_number} ({self.get_status_display()})"

