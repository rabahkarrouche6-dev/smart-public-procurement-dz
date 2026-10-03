"""Correlation ID and Tenant Context middleware."""
import uuid
import threading

_thread_locals = threading.local()

def get_current_request():
    """Retrieve the current request object from thread-local storage."""
    return getattr(_thread_locals, 'request', None)

class CorrelationIdMiddleware:
    """Attaches a unique Correlation ID to every request and response for traceability."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        correlation_id = request.headers.get('X-Correlation-ID') or request.headers.get('X-Request-ID') or str(uuid.uuid4())
        request.correlation_id = correlation_id
        _thread_locals.request = request

        response = self.get_response(request)
        response['X-Correlation-ID'] = correlation_id
        return response

class TenantContextMiddleware:
    """Enforces and extracts organization tenant context for authenticated users."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            request.current_organization = getattr(request.user, 'organization', None)
        else:
            request.current_organization = None

        return self.get_response(request)
