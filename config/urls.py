from django.urls import path, include
from core.views import frame, client_login

urlpatterns = [
    path("", frame, name="frame"),
    path("accounts/login/", client_login, name="login"),
    path("accounts/logout/", include("django.contrib.auth.urls")),  # uses LogoutView
    path("i18n/", include("django.conf.urls.i18n")),
    path("super-admin/", include("super_admin.urls")),
    path("", include("core.urls")),
]
