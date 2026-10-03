"""Centralized custom exception handler for Django REST Framework."""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Standardizes all API error responses:
    {
      "error": {
        "code": "ERROR_CODE",
        "message": "User-friendly message",
        "details": {...},
        "correlation_id": "uuid",
        "timestamp": "ISO-8601"
      }
    }
    """
    response = exception_handler(exc, context)
    request = context.get('request')
    correlation_id = getattr(request, 'correlation_id', 'unknown') if request else 'unknown'

    if response is not None:
        code = getattr(exc, 'default_code', 'API_ERROR').upper()
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, dict):
                details = exc.detail
                message = details.get('detail', str(exc))
            elif isinstance(exc.detail, list):
                details = {'errors': exc.detail}
                message = str(exc.detail[0]) if exc.detail else str(exc)
            else:
                details = {}
                message = str(exc.detail)
        else:
            details = {}
            message = str(exc)

        response.data = {
            'error': {
                'code': code,
                'message': message,
                'details': details,
                'correlation_id': correlation_id,
                'timestamp': timezone.now().isoformat()
            }
        }
    else:
        # Unhandled server exception
        logger.exception("Unhandled server exception: %s", exc, extra={'correlation_id': correlation_id})
        response = Response(
            {
                'error': {
                    'code': 'INTERNAL_SERVER_ERROR',
                    'message': 'حدث خطأ داخلي في الخادم. يرجى مراجعة معرف الارتباط.',
                    'details': {},
                    'correlation_id': correlation_id,
                    'timestamp': timezone.now().isoformat()
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
