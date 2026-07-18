from functools import wraps
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden



def role_required(*allowed_roles):
    """
    Decorator to restrict access to views based on user role.
    Usage: @role_required('dept_admin', 'super_admin')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Login required")
            if request.user.role not in allowed_roles:
                return HttpResponseForbidden("You don't have permission to access this page.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
