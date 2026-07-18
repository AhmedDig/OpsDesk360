from django.urls import path
from . import views

app_name = "super_admin"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("clients/", views.client_list, name="client_list"),
    path("clients/add/", views.client_create, name="client_create"),
    path("clients/<int:client_id>/edit/", views.client_edit, name="client_edit"),
    path(
        "clients/<int:client_id>/toggle-status/",
        views.client_toggle_status,
        name="client_toggle_status",
    ),
    path(
        "clients/<int:client_id>/features/",
        views.client_features,
        name="client_features",
    ),
    path("payments/", views.payment_list, name="payment_list"),
    path("payments/add/", views.payment_add, name="payment_add"),
    path("tickets/", views.ticket_list, name="ticket_list"),
    path("tickets/<int:ticket_id>/update/", views.ticket_update, name="ticket_update"),
    path(
        "platform-settings/",
        views.platform_settings_placeholder,
        name="platform_settings",
    ),
]
