from django.contrib.auth import authenticate, login
from django.db import connections
from django.conf import settings

def get_client_db_name(client_domain):
    from super_admin.models import Business
    try:
        business = Business.objects.get(client_domain=client_domain)
        return business.database_name
    except Business.DoesNotExist:
        return None

def authenticate_client(request, username, password, client_domain):
    db_name = get_client_db_name(client_domain)
    if not db_name:
        return None
    # Temporarily switch the connection for core models
    from django.db import router
    # We'll manually use the database alias (we'll add it dynamically)
    # For simplicity, we'll use the existing 'client' alias or create one
    # We'll assume we have a way to route queries – see middleware later