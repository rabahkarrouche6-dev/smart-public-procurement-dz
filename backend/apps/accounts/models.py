"""Custom User model with multi-role RBAC and organization tenant scoping."""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    """Custom manager using email as unique identifier."""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('يجب تحديد البريد الإلكتروني للمستخدم'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.CENTRAL_ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('يجب أن يمتلك المشرف صلاحية is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('يجب أن يمتلك المشرف صلاحية is_superuser=True'))

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model for Algerian Smart Procurement Platform."""
    class Role(models.TextChoices):
        CENTRAL_ADMIN = 'CENTRAL_ADMIN', _('مسؤول الإدارة المركزية (رقابة وتوجيه)')
        CONTRACTING_AUTHORITY_ADMIN = 'CONTRACTING_AUTHORITY_ADMIN', _('مدير المصلحة المتعاقدة')
        CONTRACTING_AUTHORITY_OFFICER = 'CONTRACTING_AUTHORITY_OFFICER', _('مقرر / مسير الصفقات')
        CONTRACTING_AUTHORITY_REVIEWER = 'CONTRACTING_AUTHORITY_REVIEWER', _('عضو لجنة فتح وتقييم العروض')
        ECONOMIC_OPERATOR_ADMIN = 'ECONOMIC_OPERATOR_ADMIN', _('مسؤول حساب المتعامل الاقتصادي')
        ECONOMIC_OPERATOR_USER = 'ECONOMIC_OPERATOR_USER', _('مفوض لتقديم العروض')
        AUDITOR = 'AUDITOR', _('مدقق ومفتش مالي')
        READ_ONLY = 'READ_ONLY', _('مطلع فقط')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("المعرف الفريد")
    )
    email = models.EmailField(
        unique=True,
        db_index=True,
        verbose_name=_("البريد الإلكتروني")
    )
    full_name = models.CharField(
        max_length=255,
        verbose_name=_("الاسم الكامل")
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name=_("رقم الهاتف")
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='members',
        verbose_name=_("المؤسسة أو الهيئة التابع لها")
    )
    role = models.CharField(
        max_length=40,
        choices=Role.choices,
        default=Role.READ_ONLY,
        db_index=True,
        verbose_name=_("الدور والصلاحية")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("الحساب نشط")
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("تم التحقق من الهوية")
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_("دخول لوحة الإدارة")
    )
    date_joined = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاريخ الانضمام")
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = _("مستخدم")
        verbose_name_plural = _("المستخدمون")
        ordering = ['-date_joined']

    def __str__(self):
        org_name = self.organization.name if self.organization else "بدون هيئة"
        return f"{self.full_name} ({self.get_role_display()} - {org_name})"

    @property
    def is_contracting_authority(self):
        return self.role in [
            self.Role.CONTRACTING_AUTHORITY_ADMIN,
            self.Role.CONTRACTING_AUTHORITY_OFFICER,
            self.Role.CONTRACTING_AUTHORITY_REVIEWER,
        ]

    @property
    def is_economic_operator(self):
        return self.role in [
            self.Role.ECONOMIC_OPERATOR_ADMIN,
            self.Role.ECONOMIC_OPERATOR_USER,
        ]

    @property
    def is_central_admin(self):
        return self.role == self.Role.CENTRAL_ADMIN
