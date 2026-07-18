from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Business, PaymentRecord, Ticket
from .forms import BusinessForm, FeatureToggleForm, PaymentForm, TicketForm
from core.utils import htmx_render


def is_super_admin(user):
    return user.is_authenticated and user.is_superuser


@login_required
@user_passes_test(is_super_admin)
def dashboard(request):
    total_clients = Business.objects.count()
    active_clients = Business.objects.filter(status="active").count()
    total_tickets = Ticket.objects.filter(status="open").count()
    recent_clients = Business.objects.order_by("-created_at")[:5]
    recent_tickets = Ticket.objects.order_by("-created_at")[:5]
    context = {
        "total_clients": total_clients,
        "active_clients": active_clients,
        "total_tickets": total_tickets,
        "recent_clients": recent_clients,
        "recent_tickets": recent_tickets,
    }
    return htmx_render(request, "partials/super_admin/dashboard.html", context)


@login_required
@user_passes_test(is_super_admin)
def client_list(request):
    clients = Business.objects.all()
    return htmx_render(
        request, "partials/super_admin/client_list.html", {"clients": clients}
    )


@login_required
@user_passes_test(is_super_admin)
def client_create(request):
    if request.method == "POST":
        form = BusinessForm(request.POST)
        if form.is_valid():
            business = form.save(commit=False)
            import re

            db_name = re.sub(r"[^a-zA-Z0-9_]", "_", business.client_domain.lower())
            business.database_name = db_name
            business.save()
            messages.success(request, f"Client {business.client_domain} created.")
            return redirect("super_admin:client_list")
    else:
        form = BusinessForm()
    return htmx_render(
        request,
        "partials/super_admin/client_form.html",
        {"form": form, "title": "Add Client"},
    )


@login_required
@user_passes_test(is_super_admin)
def client_edit(request, client_id):
    client = get_object_or_404(Business, id=client_id)
    if request.method == "POST":
        form = BusinessForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, "Client updated.")
            return redirect("super_admin:client_list")
    else:
        form = BusinessForm(instance=client)
    return htmx_render(
        request,
        "partials/super_admin/client_form.html",
        {"form": form, "title": "Edit Client"},
    )


@login_required
@user_passes_test(is_super_admin)
def client_toggle_status(request, client_id):
    client = get_object_or_404(Business, id=client_id)
    client.status = "suspended" if client.status == "active" else "active"
    client.save()
    messages.success(
        request, f"Client {client.client_domain} status changed to {client.status}."
    )
    return redirect("super_admin:client_list")


@login_required
@user_passes_test(is_super_admin)
def client_features(request, client_id):
    client = get_object_or_404(Business, id=client_id)
    if request.method == "POST":
        form = FeatureToggleForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, "Features updated.")
            return redirect("super_admin:client_list")
    else:
        form = FeatureToggleForm(instance=client)
    return htmx_render(
        request,
        "partials/super_admin/client_features.html",
        {"client": client, "form": form},
    )


@login_required
@user_passes_test(is_super_admin)
def payment_list(request):
    payments = PaymentRecord.objects.all().order_by("-recorded_at")
    return htmx_render(
        request, "partials/super_admin/payment_list.html", {"payments": payments}
    )


@login_required
@user_passes_test(is_super_admin)
def payment_add(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Payment recorded.")
            return redirect("super_admin:payment_list")
    else:
        form = PaymentForm()
    return htmx_render(
        request, "partials/super_admin/payment_form.html", {"form": form}
    )


@login_required
@user_passes_test(is_super_admin)
def ticket_list(request):
    tickets = Ticket.objects.all().order_by("-created_at")
    return htmx_render(
        request, "partials/super_admin/ticket_list.html", {"tickets": tickets}
    )


@login_required
@user_passes_test(is_super_admin)
def ticket_update(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == "POST":
        form = TicketForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, "Ticket updated.")
            return redirect("super_admin:ticket_list")
    else:
        form = TicketForm(instance=ticket)
    return htmx_render(
        request,
        "partials/super_admin/ticket_form.html",
        {"form": form, "ticket": ticket},
    )


# Placeholder for platform settings
def platform_settings_placeholder(request):
    return htmx_render(request, "partials/super_admin/platform_settings.html", {})
