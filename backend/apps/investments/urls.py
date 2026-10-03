"""Investments URL routes."""
from rest_framework.routers import DefaultRouter
from apps.investments.views import (
    BudgetViewSet,
    InvestmentEnvelopeViewSet,
    InvestmentProgramViewSet,
    InvestmentOperationViewSet,
)

router = DefaultRouter()
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'envelopes', InvestmentEnvelopeViewSet, basename='envelope')
router.register(r'programs', InvestmentProgramViewSet, basename='program')
router.register(r'operations', InvestmentOperationViewSet, basename='operation')

urlpatterns = router.urls
