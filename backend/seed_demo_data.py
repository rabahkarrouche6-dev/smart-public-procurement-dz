"""Seed script to populate initial sample data for demonstration."""
import os
import sys
from pathlib import Path
from decimal import Decimal

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.utils import timezone
from apps.organizations.models import Organization
from apps.accounts.models import User
from apps.procurements.models import Procurement
from apps.tender_documents.models import TenderDocument
from apps.documents.models import Document
from apps.bids.models import Bid
from apps.evaluations.models import EvaluationFormula, EvaluationCriterion
from apps.legal_rag.models import LegalDocument, LegalArticle
from apps.subscriptions.models import Plan, Subscription

def seed():
    print("🌱 Starting initial demo data seeding...")

    # 1. Organizations
    org_ca, _ = Organization.objects.get_or_create(
        nif="000116019000085",
        defaults={
            "name": "ولاية الجزائر - مديرية التجهيزات العمومية",
            "org_type": Organization.OrgType.CONTRACTING_AUTHORITY,
            "wilaya_code": "16",
            "address": "شارع العقيد عميروش، الجزائر العاصمة",
            "verification_status": Organization.VerificationStatus.VERIFIED,
            "data_provenance": Organization.SourceType.SAMPLE_DATA
        }
    )

    org_eo, _ = Organization.objects.get_or_create(
        nif="001816001234567",
        defaults={
            "name": "شركة الإنجازات الوطنية للأشغال الكبرى (SARL)",
            "org_type": Organization.OrgType.ECONOMIC_OPERATOR,
            "registration_number": "16/00-1234567B18",
            "wilaya_code": "16",
            "address": "المنطقة الصناعية وادي السمار، الجزائر",
            "verification_status": Organization.VerificationStatus.VERIFIED,
            "data_provenance": Organization.SourceType.SAMPLE_DATA
        }
    )

    org_admin, _ = Organization.objects.get_or_create(
        nif="000016000000001",
        defaults={
            "name": "وزارة المالية - سلطة ضبط الصفقات العمومية",
            "org_type": Organization.OrgType.CENTRAL_ADMIN,
            "wilaya_code": "16",
            "address": "حي زغود يوسف، بن عكنون، الجزائر",
            "verification_status": Organization.VerificationStatus.VERIFIED,
            "data_provenance": Organization.SourceType.SAMPLE_DATA
        }
    )

    # 2. Users
    user_ca = User.objects.filter(email="officer@alger-marches.dz").first()
    if not user_ca:
        user_ca = User.objects.create_user(
            email="officer@alger-marches.dz",
            password="ValidStrongPassword2026!",
            full_name="كريم بلقاسم (مسير الصفقات)",
            organization=org_ca,
            role=User.Role.CONTRACTING_AUTHORITY_OFFICER,
            is_staff=True
        )

    user_eo = User.objects.filter(email="bidder@injazat-algerie.dz").first()
    if not user_eo:
        user_eo = User.objects.create_user(
            email="bidder@injazat-algerie.dz",
            password="ValidStrongPassword2026!",
            full_name="سمير بن علي (مدير المناقصات)",
            organization=org_eo,
            role=User.Role.ECONOMIC_OPERATOR_USER
        )

    user_admin = User.objects.filter(email="admin@marches-publics.dz").first()
    if not user_admin:
        user_admin = User.objects.create_superuser(
            email="admin@marches-publics.dz",
            password="ValidStrongPassword2026!",
            full_name="أحمد بوعلام (المراقب العام)",
            organization=org_admin,
            role=User.Role.CENTRAL_ADMIN
        )

    # 3. Subscriptions (MVP_FREE)
    plan, _ = Plan.objects.get_or_create(
        code="MVP_FREE",
        defaults={
            "name": "النسخة التجريبية الشاملة المجانية",
            "description": "تشمل كافة وظائف الصفقات والذكاء الاصطناعي مجاناً للمرحلة التجريبية."
        }
    )
    for org in [org_ca, org_eo, org_admin]:
        Subscription.objects.get_or_create(
            organization=org,
            defaults={"plan": plan, "status": Subscription.Status.ACTIVE}
        )

    # 4. Procurement
    proc, _ = Procurement.objects.get_or_create(
        procurement_number="2026/01/DEP",
        organization=org_ca,
        defaults={
            "title": "مشروع بناء مجمع مدرسي صنف ج - بلدية الدار البيضاء",
            "description": "إنجاز 12 قاعة تدريس، إدارة، مطعم مدرسي، وفناء مهيأ بكامل التجهيزات.",
            "procedure_type": Procurement.ProcedureType.OPEN_TENDER,
            "status": Procurement.Status.BID_SUBMISSION,
            "estimated_budget": Decimal("150000000.00"),
            "publication_date": timezone.now() - timezone.timedelta(days=10),
            "submission_deadline": timezone.now() + timezone.timedelta(days=20),
            "created_by": user_ca,
            "data_provenance": Procurement.SourceType.SAMPLE_DATA
        }
    )

    # 5. Formula & Criteria
    formula, _ = EvaluationFormula.objects.get_or_create(
        procurement=proc,
        version=1,
        defaults={
            "organization": org_ca,
            "technical_weight_percent": Decimal("70.00"),
            "financial_weight_percent": Decimal("30.00"),
            "minimum_technical_threshold": Decimal("50.00"),
            "decimal_precision": 2
        }
    )
    EvaluationCriterion.objects.get_or_create(
        formula=formula,
        code="TECH_EXPERIENCE",
        defaults={"label": "الخبرة في مشاريع البناء المماثلة", "max_points": Decimal("50.00")}
    )
    EvaluationCriterion.objects.get_or_create(
        formula=formula,
        code="TECH_EQUIPMENT",
        defaults={"label": "الوسائل المادية والعتاد المخصص للورشة", "max_points": Decimal("50.00")}
    )

    # 6. Authoritative Legal Text (Loi 23-12)
    legal_doc, _ = LegalDocument.objects.get_or_create(
        official_number="23-12",
        defaults={
            "title": "القانون رقم 23-12 يحدد القواعد العامة المتعلقة بالصفقات العمومية",
            "legal_type": LegalDocument.LegalType.LAW,
            "promulgation_date": timezone.datetime(2023, 8, 5).date(),
            "joradp_reference": "الجريدة الرسمية رقم 51 المؤرخة في 6 أغسطس 2023"
        }
    )
    LegalArticle.objects.get_or_create(
        document=legal_doc,
        article_number="5",
        defaults={
            "title": "المبادئ الأساسية للصفقات العمومية",
            "content_ar": "تخضع الصفقات العمومية للمبادئ الآتية: حرية الوصول للطلبات العمومية، والمساواة في معاملة المرشحين، وشفافية الإجراءات في إطار احترام البيئة وأهداف التنمية المستدامة.",
            "content_fr": "Les marchés publics sont soumis aux principes suivants : la liberté d'accès à la commande publique, l'égalité de traitement des candidats et la transparence des procédures.",
            "keywords": ["مبادئ", "شفافية", "مساواة", "حرية الوصول"]
        }
    )
    LegalArticle.objects.get_or_create(
        document=legal_doc,
        article_number="67",
        defaults={
            "title": "محتوى عروض المتعهدين وإجراءات الإيداع",
            "content_ar": "تشتمل العروض على ملف الترشح، وعرض تقني، وعرض مالي. يوضع كل ملف في ظرف منفصل ومقفل بإحكام يوضح تسمية المؤسسة وموضوع الصفقة.",
            "content_fr": "Les offres comprennent un dossier de candidature, une offre technique et une offre financière scellés séparément.",
            "keywords": ["ملف الترشح", "العرض التقني", "العرض المالي", "الأظرفة"]
        }
    )

    print("✅ Initial demo data seeded successfully!")

if __name__ == '__main__':
    seed()
