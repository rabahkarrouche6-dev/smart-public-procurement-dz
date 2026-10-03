"""Execution URL routes."""
from rest_framework.routers import DefaultRouter
from apps.execution.views import (
    ServiceOrderViewSet,
    ExecutionMilestoneViewSet,
    ProgressRecordViewSet,
    PaymentRecordViewSet,
)

router = DefaultRouter()
router.register(r'service-orders', ServiceOrderViewSet, basename='service-order')
router.register(r'milestones', ExecutionMilestoneViewSet, basename='execution-milestone')
router.register(r'progress', ProgressRecordViewSet, basename='progress-record')
router.register(r'payments', PaymentRecordViewSet, basename='payment-record')

urlpatterns = router.urls
