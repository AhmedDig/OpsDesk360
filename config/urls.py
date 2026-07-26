from django.urls import path, include
from core.views import frame, client_login
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", frame, name="frame"),
    path("accounts/login/", client_login, name="login"),
    path("accounts/logout/", include("django.contrib.auth.urls")),  # uses LogoutView
    path("i18n/", include("django.conf.urls.i18n")),
    path("super-admin/", include("super_admin.urls")),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
