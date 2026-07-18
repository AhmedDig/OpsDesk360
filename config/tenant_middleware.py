# config/tenant_middleware.py
from core.thread_local import set_current_business, set_current_is_superuser

class BusinessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            set_current_business(request.user.business)
            set_current_is_superuser(request.user.is_superuser)
        else:
            set_current_business(None)
            set_current_is_superuser(False)
        response = self.get_response(request)
        set_current_business(None)
        set_current_is_superuser(False)
        return response