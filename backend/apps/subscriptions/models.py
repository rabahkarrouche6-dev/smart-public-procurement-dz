"""Subscription, Feature Entitlement, and Usage models."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import BaseModel

class Plan(BaseModel):
    """SaaS plan definition (MVP_FREE, PRO, ENTERPRISE)."""
    code = models.CharField(max_length=50, unique=True, verbose_name=_("رمز الخطة"))
    name = models.CharField(max_length=100, verbose_name=_("اسم الخطة"))
    description = models.TextField(blank=True, verbose_name=_("الوصف"))
    is_active = models.BooleanField(default=True, verbose_name=_("مفعلة"))

    def __str__(self):
        return f"{self.name} ({self.code})"

class Feature(BaseModel):
    """Feature or capability key (e.g., ai.ocr, ai.legal_rag, export.analytics)."""
    key = models.CharField(max_length=100, unique=True, verbose_name=_("مفتاح الميزة"))
    name = models.CharField(max_length=150, verbose_name=_("اسم الميزة"))
    description = models.TextField(blank=True, verbose_name=_("الوصف"))

    def __str__(self):
        return f"{self.name} [{self.key}]"

class Subscription(BaseModel):
    """Active subscription binding an Organization to a Plan."""
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', _('نشط')
        TRIAL = 'TRIAL', _('تجريبي')
        EXPIRED = 'EXPIRED', _('منتهي')
        SUSPENDED = 'SUSPENDED', _('معلق')

    organization = models.OneToOneField(
        'organizations.Organization',
        on_delete=models.PROTECT,
        related_name='subscription',
        verbose_name=_("المؤسسة المشتركة")
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='subscriptions',
        verbose_name=_("الخطة المعتمدة")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_("حالة الاشتراك")
    )
    starts_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ البدء"))
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_("تاريخ الانتهاء"))

    def __str__(self):
        return f"Subscription for {self.organization.name} - {self.plan.name} ({self.status})"

class Entitlement(BaseModel):
    """Specific feature permission granted to a plan or subscription."""
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='entitlements')
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name='plan_entitlements')
    limit_value = models.IntegerField(default=-1, help_text="-1 signifies unlimited")

    class Meta:
        unique_together = ('plan', 'feature')

    def __str__(self):
        return f"{self.plan.code} -> {self.feature.key} (Limit: {self.limit_value})"

class UsageRecord(BaseModel):
    """Tracks consumption (e.g. AI tokens, documents processed) for quota auditing."""
    organization = models.ForeignKey('organizations.Organization', on_delete=models.PROTECT, related_name='usage_records')
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    feature = models.ForeignKey(Feature, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)
    recorded_at = models.DateTimeField(auto_now_add=True)
