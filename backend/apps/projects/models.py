"""Project models linked to investment operations."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import TenantScopedModel

class Project(TenantScopedModel):
    """Infrastructure or acquisition project attached to an investment operation."""
    code = models.CharField(
        max_length=50,
        db_index=True,
        verbose_name=_("رمز المشروع")
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("اسم المشروع")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("تفاصيل وأهداف المشروع")
    )
    program = models.ForeignKey(
        'investments.InvestmentProgram',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='projects',
        verbose_name=_("البرنامج الاستثماري المرتبط")
    )
    operation = models.ForeignKey(
        'investments.InvestmentOperation',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='projects',
        verbose_name=_("العملية الاستثمارية المرتبطة")
    )
    estimated_cost = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default=0,
        verbose_name=_("التكلفة التقديرية الإجمالية (دج)")
    )

    class Meta:
        verbose_name = _("مشروع")
        verbose_name_plural = _("المشاريع")
        unique_together = ('organization', 'code')
        constraints = [
            models.CheckConstraint(
                condition=models.Q(estimated_cost__gte=0),
                name='positive_project_cost'
            )
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"
