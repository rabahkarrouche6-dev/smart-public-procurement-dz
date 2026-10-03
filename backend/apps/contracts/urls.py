"""Contracts URL routes."""
from rest_framework.routers import DefaultRouter
from apps.contracts.views import ContractViewSet, ContractMilestoneViewSet

router = DefaultRouter()
router.register(r'milestones', ContractMilestoneViewSet, basename='contract-milestone')
router.register(r'', ContractViewSet, basename='contract')

urlpatterns = router.urls
