from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def navigation(request):
    if not request.user.is_authenticated:
        return {"menu_groups": []}
    user = request.user
    business = getattr(user, "business", None)
    features = business.features if business else {}
    is_super = user.is_superuser

    def item(name, url_name, icon, condition=True):
        if condition:
            try:
                url = reverse(url_name)
            except:
                url = "#"
            return {"name": name, "url": url, "icon": icon, "locked": False}
        return None

    def locked(name, description, icon):
        return {
            "name": name,
            "url": "#",
            "icon": icon,
            "locked": True,
            "description": description,
        }

    menu = []

    # 🏠 Main
    main_items = [item(_("Dashboard"), "dashboard", "tachometer")]
    menu.append({"title": _("Main"), "items": main_items, "is_group": False})

    # 🔑 Core Operations
    core_items = [
        item(_("POS"), "pos_home", "shopping-cart"),
        item(_("Catalog"), "catalog_list", "tag"),
        item(_("Customers"), "customer_list", "user"),
        item(_("Employees"), "employee_list", "users"),
    ]
    menu.append({"title": _("Core Operations"), "items": core_items, "is_group": False})

    # 💰 Sales (collapsible group with sub-items)
    sales_items = [
        item(_("Invoices"), "sales_list", "file-invoice"),
        item(_("Discounts"), "discounts_list", "tag"),
        item(_("Gift Cards"), "gift_cards_list", "gift"),
    ]
    menu.append({"title": _("Sales"), "items": sales_items, "is_group": True})

    # 📅 Business Management (add‑ons)
    biz_items = []
    if features.get("appointments", False):
        biz_items.append(
            item(_("Appointments"), "appointments_schedule", "calendar-alt")
        )
    else:
        biz_items.append(
            locked(
                _("Appointments"), _("Schedule, staff view, reminders"), "calendar-alt"
            )
        )
    if features.get("reports", False):
        biz_items.append(item(_("Reports & Analytics"), "reports_sales", "chart-line"))
    else:
        biz_items.append(
            locked(
                _("Reports & Analytics"),
                _("Sales, inventory, profitability, taxes"),
                "chart-line",
            )
        )
    if features.get("loyalty", False):
        biz_items.append(item(_("Loyalty Program"), "loyalty_points", "gift"))
    else:
        biz_items.append(
            locked(_("Loyalty Program"), _("Points, rewards, tiers"), "gift")
        )
    if features.get("marketing", False):
        biz_items.append(item(_("Marketing"), "marketing_campaigns", "bullhorn"))
    else:
        biz_items.append(
            locked(_("Marketing"), _("Campaigns, email/SMS, reviews"), "bullhorn")
        )
    if features.get("accounting", False):
        biz_items.append(item(_("Accounting"), "accounting_expenses", "calculator"))
    else:
        biz_items.append(
            locked(_("Accounting"), _("Expenses, profit/loss"), "calculator")
        )
    if features.get("multi_branch", False):
        biz_items.append(
            item(_("Multi‑Branch"), "multibranch_inventory_transfer", "store")
        )
    else:
        biz_items.append(
            locked(
                _("Multi‑Branch"),
                _("Inventory transfer, cross‑location reports"),
                "store",
            )
        )
    if biz_items:
        menu.append(
            {"title": _("Business Management"), "items": biz_items, "is_group": False}
        )

    # ⚙️ System & Settings
    sys_items = [
        item(_("Company Settings"), "company_settings", "sliders-h"),
        item(
            _("User Management"),
            "user_list",
            "user-cog",
            condition=is_super or user.role == "dept_admin",
        ),
        item(_("Integrations"), "integrations_home", "plug"),
        item(_("Backup & Restore"), "backup_restore", "database"),
    ]
    menu.append(
        {"title": _("System & Settings"), "items": sys_items, "is_group": False}
    )

    # 🧩 Add‑On Modules (Locked)
    addon_items = [
        locked(
            _("Medical Records"),
            _("For clinics: EHR, appointments, prescriptions"),
            "stethoscope",
        ),
        locked(_("Field Service"), _("Work orders, technician dispatch"), "truck"),
        locked(_("E‑Commerce"), _("Online store, sync inventory"), "cart-plus"),
        locked(
            _("Rental Management"),
            _("Pricing, availability, agreements"),
            "calendar-check",
        ),
        locked(_("Restaurant"), _("Tables, split bills, kitchen display"), "utensils"),
    ]
    menu.append(
        {"title": _("Add‑On Modules (Locked)"), "items": addon_items, "is_group": False}
    )

    # 🛠️ Super Admin
    if is_super:
        sa_items = [
            item(_("Dashboard"), "super_admin:dashboard", "tachometer-alt"),
            item(_("Clients"), "super_admin:client_list", "building"),
            item(_("Payments"), "super_admin:payment_list", "money-bill-wave"),
            item(_("Support Tickets"), "super_admin:ticket_list", "ticket-alt"),
            item(_("Platform Settings"), "super_admin:platform_settings", "cog"),
        ]
        menu.append({"title": _("Super Admin"), "items": sa_items, "is_group": False})

    return {"menu_groups": menu}


def business_context(request):
    if request.user.is_authenticated and request.user.business:
        return {"business": request.user.business}
    return {"business": None}
