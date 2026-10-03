"""Investment, Budget, Envelopes, Programs, and Operation models for Algerian public procurement."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import TenantScopedModel

class Budget(TenantScopedModel):
    """Annual institutional budget allocation."""
    fiscal_year = models.PositiveIntegerField(
        db_index=True,
        verbose_name=_("السنة المالية")
    )
    initial_allocation = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name=_("الاعتماد المالي المبدئي (دج)")
    )
    current_allocation = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name=_("الاعتماد المالي الحالي (دج)")
    )
    committed_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name=_("المبالغ الملتزم بها (دج)")
    )

    class Meta:
        verbose_name = _("ميزانية سنوية")
        verbose_name_plural = _("الميزانيات السنوية")
        unique_together = ('organization', 'fiscal_year')
        constraints = [
            models.CheckConstraint(
                condition=models.Q(initial_allocation__gte=0) & models.Q(current_allocation__gte=0) & models.Q(committed_amount__gte=0),
                name='positive_budget_amounts'
            )
        ]

    def __str__(self):
        return f"Budget {self.fiscal_year} - {self.organization.name}"


class InvestmentEnvelope(TenantScopedModel):
    """
    Investment Envelope (غلاف مالي استثماري - Enveloppe budgétaire).
    Attached to a Budget allocation.
    """
    budget = models.ForeignKey(
        Budget,
        on_delete=models.PROTECT,
        related_name='envelopes',
        verbose_name=_("الميزانية المعنية")
    )
    code = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name=_("رمز الغلاف المالي")
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("عنوان الغلاف المالي")
    )
    allocated_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name=_("المبلغ المخصص للغلاف (دج)")
    )
    consumed_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name=_("المبلغ المستهلك (دج)")
    )

    class Meta:
        verbose_name = _("غلاف مالي استثماري")
        verbose_name_plural = _("الأغلفة المالية الاستثمارية")
        unique_together = ('organization', 'code')
        constraints = [
            models.CheckConstraint(
                condition=models.Q(allocated_amount__gte=0) & models.Q(consumed_amount__gte=0),
                name='positive_envelope_amounts'
            )
        ]

    def __str__(self):
        return f"{self.code} - {self.title}"


class InvestmentProgram(TenantScopedModel):
    """
    Investment Program (برنامج استثماري - Programme d'Investissement).
    Attached to an Investment Envelope.
    Types: PCD (Communal), PSD (Sectoriel Déconcentré), PSC (Centralisé/National), EQUIPMENT.
    """
    class ProgramType(models.TextChoices):
        PCD = 'PCD', _('مخطط بلدي للتنمية (PCD)')
        PSD = 'PSD', _('برنامج قطاعي غير ممركز (PSD)')
        PSC = 'PSC', _('برنامج قطاعي ممركز (PSC)')
        EQUIPMENT = 'EQUIPMENT', _('برنامج تجهيز عمومي')

    envelope = models.ForeignKey(
        InvestmentEnvelope,
        on_delete=models.PROTECT,
        related_name='programs',
        verbose_name=_("الغلاف المالي المرتبط")
    )
    code = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name=_("رمز البرنامج الاستثماري")
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("عنوان البرنامج الاستثماري")
    )
    program_type = models.CharField(
        max_length=30,
        choices=ProgramType.choices,
        default=ProgramType.EQUIPMENT,
        verbose_name=_("طبيعة ونوع البرنامج")
    )
    allocated_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name=_("المبلغ المخصص للبرنامج (دج)")
    )

    class Meta:
        verbose_name = _("برنامج استثماري")
        verbose_name_plural = _("البرامج الاستثمارية")
        unique_together = ('organization', 'code')
        constraints = [
            models.CheckConstraint(
                condition=models.Q(allocated_amount__gte=0),
                name='positive_program_amounts'
            )
        ]

    def __str__(self):
        return f"{self.code} - {self.title} ({self.get_program_type_display()})"


class InvestmentOperation(TenantScopedModel):
    """
    Public equipment investment operation (Fiche d'Opération d'Équipement Public).
    Tracks AP (Autorisation de Programme) and CP (Crédits de Paiement).
    """
    operation_number = models.CharField(
        max_length=60,
        unique=True,
        db_index=True,
        verbose_name=_("رقم تسجيل العملية (N° Opération)")
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("عنوان العملية الاستثمارية")
    )
    budget = models.ForeignKey(
        Budget,
        on_delete=models.PROTECT,
        related_name='operations',
        verbose_name=_("الميزانية المرتبطة")
    )
    program = models.ForeignKey(
        InvestmentProgram,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='operations',
        verbose_name=_("البرنامج الاستثماري")
    )
    program_authorization = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name=_("رخصة البرنامج (AP - Autorisation de Programme)")
    )
    payment_credits = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name=_("اعتمادات الدفع (CP - Crédits de Paiement)")
    )

    class Meta:
        verbose_name = _("عملية استثمارية عمومية")
        verbose_name_plural = _("العمليات الاستثمارية")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(program_authorization__gte=0) & models.Q(payment_credits__gte=0),
                name='positive_operation_amounts'
            )
        ]

    def __str__(self):
        return f"{self.operation_number}: {self.title}"
