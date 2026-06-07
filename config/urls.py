from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views as core_views  # <-- add this line

urlpatterns = [
    # Language switching
    path("i18n/", include("django.conf.urls.i18n")),
    # Authentication
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    # Core URLs
    path("", core_views.dashboard, name="dashboard"),
    path("categories/", core_views.category_list, name="category_list"),
    path("categories/create/", core_views.category_create, name="category_create"),
    path("categories/edit/<int:pk>/", core_views.category_edit, name="category_edit"),
    path(
        "categories/delete/<int:pk>/",
        core_views.category_delete,
        name="category_delete",
    ),
    path("items/", core_views.item_list, name="item_list"),
    path("items/create/", core_views.item_create, name="item_create"),
    path("items/edit/<int:pk>/", core_views.item_edit, name="item_edit"),
    path("items/delete/<int:pk>/", core_views.item_delete, name="item_delete"),
    path("customers/", core_views.customer_list, name="customer_list"),
    path("customers/create/", core_views.customer_create, name="customer_create"),
    path("customers/edit/<int:pk>/", core_views.customer_edit, name="customer_edit"),
    path(
        "customers/delete/<int:pk>/", core_views.customer_delete, name="customer_delete"
    ),
    path("users/", core_views.user_list, name="user_list"),
    path("users/create/", core_views.user_create, name="user_create"),
    path("super-admin/", include("super_admin.urls")),
]
