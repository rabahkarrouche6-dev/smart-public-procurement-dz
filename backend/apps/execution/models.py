"""Execution phase models (ODS, Milestones, Situations/Payments, Attachments)."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import TenantScopedModel

class ServiceOrder(TenantScopedModel):
    """Service Order (أمر بالخدمة - Ordre de Service ODS) issued during execution."""
    class OdsType(models.TextChoices):
        COMMENCE_WORK = 'COMMENCE_WORK', _('أمر ببداية الأشغال أو الخدمات')
        STOP_WORK = 'STOP_WORK', _('أمر بتوقيف الأشغال')
        RESUME_WORK = 'RESUME_WORK', _('أمر باستئناف الأشغال')

    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.PROTECT,
        related_name='service_orders',
        verbose_name=_("العقد المعني")
    )
    ods_number = models.CharField(
        max_length=50,
        verbose_name=_("رقم الأمر بالخدمة")
    )
    ods_type = models.CharField(
        max_length=30,
        choices=OdsType.choices,
        verbose_name=_("نوع الأمر بالخدمة")
    )
    issue_date = models.DateField(
        verbose_name=_("تاريخ الإصدار")
    )
    effective_date = models.DateField(
        verbose_name=_("تاريخ السريان والنفاذ")
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("ملاحظات وتوجيهات")
    )

    class Meta:
        verbose_name = _("أمر بالخدمة (ODS)")
        verbose_name_plural = _("أوامر الخدمة")
        ordering = ['-issue_date']

    def __str__(self):
        return f"ODS {self.ods_number} ({self.get_ods_type_display()}) - {self.contract.contract_number}"


class ExecutionMilestone(TenantScopedModel):
    """Execution progress milestone."""
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('قيد الانتظار')
        IN_PROGRESS = 'IN_PROGRESS', _('قيد التنفيذ')
        COMPLETED = 'COMPLETED', _('مكتملة')
        DELAYED = 'DELAYED', _('متأخرة عن الجدول')

    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='execution_milestones',
        verbose_name=_("العقد المعني")
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("عنوان المرحلة الميدانية")
    )
    target_completion_date = models.DateField(
        verbose_name=_("تاريخ الإنجاز المستهدف")
    )
    actual_completion_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("تاريخ الإنجاز الفعلي")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("حالة المرحلة")
    )
    progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name=_("نسبة الإنجاز المحققة (%)")
    )

    class Meta:
        verbose_name = _("مرحلة تنفيذ")
        verbose_name_plural = _("مراحل التنفيذ")
        ordering = ['target_completion_date']

    def __str__(self):
        return f"{self.title} - {self.contract.contract_number} ({self.get_status_display()})"


class ProgressRecord(TenantScopedModel):
    """
    Physical & Financial Progress Record (كشف تقدم الأشغال - Attachement d'avancement).
    """
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='progress_records',
        verbose_name=_("العقد المعني")
    )
    record_number = models.CharField(
        max_length=50,
        verbose_name=_("رقم كشف التقدم / المحضر")
    )
    record_date = models.DateField(
        verbose_name=_("تاريخ الكشف أو المعاينة")
    )
    physical_progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("نسبة التقدم المادي (%)")
    )
    financial_progress_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("نسبة التقدم المالي (%)")
    )
    cumulative_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name=_("المبلغ التراكمي المنجز (دج)")
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("ملاحظات المعاينة الميدانية")
    )

    class Meta:
        verbose_name = _("كشف تقدم الأشغال")
        verbose_name_plural = _("كشوفات تقدم الأشغال")
        ordering = ['-record_date']

    def __str__(self):
        return f"Progress {self.record_number} ({self.physical_progress_percentage}%) - {self.contract.contract_number}"


class PaymentRecord(TenantScopedModel):
    """
    Payment Record / Situation / Décompte (وضعية الدفع / كشف الحساب).
    """
    class PaymentStatus(models.TextChoices):
        DRAFT = 'DRAFT', _('مسودة')
        SUBMITTED = 'SUBMITTED', _('مقدمة للمصلحة المتعاقدة')
        VALIDATED = 'VALIDATED', _('مصادق عليها من مصلحة المحاسبة')
        PAID = 'PAID', _('مدفوعة ومسددة')
        REJECTED = 'REJECTED', _('مرفوضة لوجود تحفظات')

    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='payment_records',
        verbose_name=_("العقد المعني")
    )
    situation_number = models.CharField(
        max_length=50,
        verbose_name=_("رقم كشف الحساب (N° Situation)")
    )
    period_start = models.DateField(
        verbose_name=_("بداية الفترة المشمولة")
    )
    period_end = models.DateField(
        verbose_name=_("نهاية الفترة المشمولة")
    )
    amount_requested = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name=_("المبلغ المطلوب للصرف (دج)")
    )
    amount_approved = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name=_("المبلغ المصادق عليه (دج)")
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.DRAFT,
        verbose_name=_("حالة كشف الحساب")
    )
    payment_order_reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("رقم حوالة الدفع (Mandat de paiement)")
    )

    class Meta:
        verbose_name = _("كشف حساب مالي / وضعية دفع")
        verbose_name_plural = _("كشوفات الحساب والدفع")
        ordering = ['-period_end']

    def __str__(self):
        return f"Situation {self.situation_number} ({self.amount_requested} DZD) - {self.get_status_display()}"
