# core/auth_backends.py
from django.contrib.auth.backends import ModelBackend
from .models import User
from super_admin.models import Business

class ClientDatabaseBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, client_domain=None, **kwargs):
        if not client_domain:
            return None
        try:
            business = Business.objects.get(client_domain=client_domain)
        except Business.DoesNotExist:
            return None
        try:
            user = User.objects.get(username=username, business=business)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        return None