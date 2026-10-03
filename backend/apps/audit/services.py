"""Audit recording domain service."""
from apps.audit.models import AuditLog
from apps.common.middleware import get_current_request

def record_audit_event(
    action: str,
    resource_type: str,
    resource_id: str,
    actor=None,
    organization=None,
    old_values=None,
    new_values=None,
    result=AuditLog.ResultStatus.SUCCESS,
    request=None
) -> AuditLog:
    """
    Creates an immutable audit log record.
    If request is omitted, attempts to recover context from thread-local storage.
    """
    if request is None:
        request = get_current_request()

    actor_user = actor or (request.user if request and request.user.is_authenticated else None)
    actor_email = actor_user.email if actor_user else "system"
    org = organization or (actor_user.organization if actor_user and hasattr(actor_user, 'organization') else None)
    
    correlation_id = getattr(request, 'correlation_id', '') if request else ''
    ip_address = None
    user_agent = ''

    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

    return AuditLog.objects.create(
        actor=actor_user,
        actor_email=actor_email,
        organization=org,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
        old_values=old_values,
        new_values=new_values,
        correlation_id=correlation_id,
        ip_address=ip_address,
        user_agent=user_agent,
        result=result
    )
