"""Organization and Tenant models representing Algerian public institutions and economic operators."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import BaseModel, ProvenanceModel

class Organization(BaseModel, ProvenanceModel):
    """
    Organization entity defining tenant boundaries across the 3 portals.
    """
    class OrgType(models.TextChoices):
        CONTRACTING_AUTHORITY = 'CONTRACTING_AUTHORITY', _('مصلحة متعاقدة (إدارة / مؤسسة عمومية)')
        ECONOMIC_OPERATOR = 'ECONOMIC_OPERATOR', _('متعامل اقتصادي (مؤسسة / شركة)')
        CENTRAL_ADMIN = 'CENTRAL_ADMIN', _('إدارة مركزية (هيئة رقابة وتوجيه)')

    class VerificationStatus(models.TextChoices):
        GOVERNMENT_VERIFIED = 'GOVERNMENT_VERIFIED', _('محققة ومعتمدة حكومياً')
        AVAILABLE_BY_API = 'AVAILABLE_BY_API', _('متاحة عبر الربط البيني الحكومي (API)')
        AVAILABLE_BY_SECURE_QUERY = 'AVAILABLE_BY_SECURE_QUERY', _('متاحة عبر الاستعلام المؤمن')
        USER_UPLOAD_REQUIRED = 'USER_UPLOAD_REQUIRED', _('تتطلب رفع وثائق ثبوتية')
        NOT_YET_CONNECTED = 'NOT_YET_CONNECTED', _('غير متصل بالقاعدة المركزية بعد')
        PENDING = 'PENDING', _('قيد التحقق والتأكيد')
        VERIFIED = 'VERIFIED', _('محققة ومعتمدة')
        REJECTED = 'REJECTED', _('مرفوضة')

    name = models.CharField(
        max_length=255,
        verbose_name=_("الاسم الرسمي للهيئة أو المؤسسة")
    )
    legal_representative = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("الممثل القانوني / المفوض بالتوقيع")
    )
    org_type = models.CharField(
        max_length=30,
        choices=OrgType.choices,
        db_index=True,
        verbose_name=_("طبيعة ونوع الهيئة")
    )
    # Fiscal identification number (NIF)
    nif = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("رقم التعريف الجبائي (NIF)")
    )
    # Commercial register (RC) or official decree reference
    registration_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("السجل التجاري أو مرسوم الإنشاء")
    )
    # Statistical identification number (NIS)
    nis = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name=_("رقم التعريف الإحصائي (NIS)")
    )
    legal_status = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("الشكل القانوني")
    )
    wilaya_code = models.CharField(
        max_length=2,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("رمز الولاية (01-58)")
    )
    address = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("العنوان الرئيسي")
    )
    phone = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name=_("الهاتف")
    )
    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_("البريد الإلكتروني الرسمي")
    )
    website = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("الموقع الإلكتروني")
    )
    verification_status = models.CharField(
        max_length=35,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
        db_index=True,
        verbose_name=_("حالة التدقيق والتحقق")
    )

    class Meta:
        verbose_name = _("هيئة / مؤسسة")
        verbose_name_plural = _("الهيئات والمؤسسات")
        ordering = ['name']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(org_type__in=['CONTRACTING_AUTHORITY', 'ECONOMIC_OPERATOR', 'CENTRAL_ADMIN']),
                name='valid_org_type'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.get_org_type_display()})"
