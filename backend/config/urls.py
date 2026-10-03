"""URL configuration for Smart Public Procurement Platform."""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from apps.common.views import FrontendPortalView

urlpatterns = [
    path('', FrontendPortalView.as_view(), name='frontend-portal'),
    path('admin/', admin.site.urls),
    
    # OpenAPI Schema & Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API v1 Versioned Routes
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/organizations/', include('apps.organizations.urls')),
    path('api/v1/investments/', include('apps.investments.urls')),
    path('api/v1/projects/', include('apps.projects.urls')),
    path('api/v1/procurements/', include('apps.procurements.urls')),
    path('api/v1/tender-documents/', include('apps.tender_documents.urls')),
    path('api/v1/bids/', include('apps.bids.urls')),
    path('api/v1/evaluations/', include('apps.evaluations.urls')),
    path('api/v1/contracts/', include('apps.contracts.urls')),
    path('api/v1/execution/', include('apps.execution.urls')),
    path('api/v1/reception/', include('apps.reception.urls')),
    path('api/v1/documents/', include('apps.documents.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/subscriptions/', include('apps.subscriptions.urls')),
    path('api/v1/audit/', include('apps.audit.urls')),
    path('api/v1/ai/', include('apps.ai_gateway.urls')),
    path('api/v1/legal/', include('apps.legal_rag.urls')),
]
