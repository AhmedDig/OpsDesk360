from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    # Profile & Settings
    path("settings/account/", views.settings_account, name="settings_account"),
    path(
        "settings/change-password/",
        views.change_password_ajax,
        name="change_password_ajax",
    ),
    # Settings
    path("settings/", views.settings_container, name="settings_container"),
    path("settings/platform/", views.settings_platform, name="settings_platform"),
    path("settings/business/", views.settings_business, name="settings_business"),
    path("settings/account/", views.settings_account, name="settings_account"),
    path(
        "settings/change-password/",
        views.change_password_ajax,
        name="change_password_ajax",
    ),
    # Categories
    path("categories/", views.category_list, name="category_list"),
    path("categories/create/", views.category_create, name="category_create"),
    path("categories/edit/<int:pk>/", views.category_edit, name="category_edit"),
    path("categories/delete/<int:pk>/", views.category_delete, name="category_delete"),
    # Catalog (merged items + inventory)
    path("catalog/", views.catalog_list, name="catalog_list"),
    path("catalog/create/", views.catalog_create, name="catalog_create"),
    path("catalog/edit/<int:pk>/", views.catalog_edit, name="catalog_edit"),
    path("catalog/delete/<int:pk>/", views.catalog_delete, name="catalog_delete"),
    path(
        "catalog/adjust-stock/<int:pk>/",
        views.catalog_adjust_stock,
        name="catalog_adjust_stock",
    ),
    # Customers
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/create/", views.customer_create, name="customer_create"),
    path("customers/edit/<int:pk>/", views.customer_edit, name="customer_edit"),
    path("customers/delete/<int:pk>/", views.customer_delete, name="customer_delete"),
    # Users
    path("users/", views.user_list, name="user_list"),
    path("users/create/", views.user_create, name="user_create"),
    path("users/<int:pk>/edit/", views.user_edit, name="user_edit"),
    # POS
    path("pos/", views.pos_home, name="pos_home"),
    path("pos/orders/", views.active_orders_list, name="active_orders_list"),
    path("pos/orders/create/", views.create_order, name="create_order"),
    path("pos/orders/switch/<int:order_id>/", views.switch_order, name="switch_order"),
    path("pos/orders/delete/<int:order_id>/", views.delete_order, name="delete_order"),
    path(
        "pos/orders/note/<int:order_id>/",
        views.update_order_note,
        name="update_order_note",
    ),
    path("pos/orders/split/<int:order_id>/", views.split_order, name="split_order"),
    path("pos/add-to-cart/", views.add_to_cart, name="add_to_cart"),
    path("pos/update-cart-item/", views.update_cart_item, name="update_cart_item"),
    path("pos/remove-cart-item/", views.remove_cart_item, name="remove_cart_item"),
    path("pos/clear-cart/", views.clear_cart, name="clear_cart"),
    path("pos/checkout/", views.checkout, name="checkout"),
    path("pos/receipt/<int:sale_id>/", views.pos_receipt, name="pos_receipt"),
    path("pos/customers/search/", views.customer_search, name="customer_search"),
    path(
        "pos/orders/discount/<int:order_id>/",
        views.update_order_discount,
        name="update_order_discount",
    ),
    path(
        "pos/orders/tax/<int:order_id>/",
        views.update_order_tax,
        name="update_order_tax",
    ),
    path("pos/product-grid/", views.render_product_grid, name="product_grid"),
    path("pos/products/", views.product_grid, name="product_grid"),
    path("pos/services/", views.service_grid, name="service_grid"),
    path(
        "pos/orders/customer/<int:order_id>/",
        views.update_order_customer,
        name="update_order_customerr",
    ),
    # Sales (placeholders)
    path("sales/", views.sales_list, name="sales_list"),
    path("sales/<int:sale_id>/", views.sale_detail, name="sale_detail"),
    path("sales/<int:sale_id>/return/", views.return_sale, name="return_sale"),
    path("discounts/", views.discounts_list, name="discounts_list"),
    path("discounts/create/", views.discount_create, name="discount_create"),
    path("discounts/edit/<int:pk>/", views.discount_edit, name="discount_edit"),
    path("discounts/delete/<int:pk>/", views.discount_delete, name="discount_delete"),
    path("gift-cards/", views.gift_cards_list, name="gift_cards_list"),
    path("gift-cards/create/", views.gift_card_create, name="gift_card_create"),
    path(
        "gift-cards/redeem/<int:pk>/", views.gift_card_redeem, name="gift_card_redeem"
    ),
    path(
        "gift-cards/delete/<int:pk>/", views.gift_card_delete, name="gift_card_delete"
    ),
    # Employees
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/create/", views.employee_create, name="employee_create"),
    path("employees/<int:pk>/edit/", views.employee_edit, name="employee_edit"),
    path("employees/<int:pk>/delete/", views.employee_delete, name="employee_delete"),
    path("employees/<int:pk>/", views.employee_detail, name="employee_detail"),
    path("employees/clock/", views.employee_clock, name="employee_clock"),
    # Appointments
    path(
        "appointments/schedule/",
        views.placeholder,
        {"template": "appointments/schedule.html"},
        name="appointments_schedule",
    ),
    path(
        "appointments/staff-view/",
        views.placeholder,
        {"template": "appointments/staff_view.html"},
        name="appointments_staff_view",
    ),
    path(
        "appointments/customer-booking/",
        views.placeholder,
        {"template": "appointments/customer_booking.html"},
        name="appointments_customer_booking",
    ),
    path(
        "appointments/reminders/",
        views.placeholder,
        {"template": "appointments/reminders.html"},
        name="appointments_reminders",
    ),
    # Reports
    path(
        "reports/sales/",
        views.placeholder,
        {"template": "reports/sales_report.html"},
        name="reports_sales",
    ),
    path(
        "reports/inventory/",
        views.placeholder,
        {"template": "reports/inventory_report.html"},
        name="reports_inventory",
    ),
    path(
        "reports/profitability/",
        views.placeholder,
        {"template": "reports/profitability.html"},
        name="reports_profitability",
    ),
    path(
        "reports/taxes/",
        views.placeholder,
        {"template": "reports/taxes.html"},
        name="reports_taxes",
    ),
    # Loyalty
    path(
        "loyalty/points/",
        views.placeholder,
        {"template": "loyalty/points.html"},
        name="loyalty_points",
    ),
    path(
        "loyalty/rewards/",
        views.placeholder,
        {"template": "loyalty/rewards.html"},
        name="loyalty_rewards",
    ),
    path(
        "loyalty/tiers/",
        views.placeholder,
        {"template": "loyalty/tiers.html"},
        name="loyalty_tiers",
    ),
    # Marketing
    path(
        "marketing/campaigns/",
        views.placeholder,
        {"template": "marketing/campaigns.html"},
        name="marketing_campaigns",
    ),
    path(
        "marketing/email-sms/",
        views.placeholder,
        {"template": "marketing/email_sms.html"},
        name="marketing_email_sms",
    ),
    path(
        "marketing/reviews/",
        views.placeholder,
        {"template": "marketing/reviews.html"},
        name="marketing_reviews",
    ),
    # Accounting
    path(
        "accounting/expenses/",
        views.placeholder,
        {"template": "accounting/expenses.html"},
        name="accounting_expenses",
    ),
    path(
        "accounting/profit-loss/",
        views.placeholder,
        {"template": "accounting/profit_loss.html"},
        name="accounting_profit_loss",
    ),
    # Multi‑Branch
    path(
        "multi-branch/inventory-transfer/",
        views.placeholder,
        {"template": "multi_branch/inventory_transfer.html"},
        name="multibranch_inventory_transfer",
    ),
    path(
        "multi-branch/cross-location-reports/",
        views.placeholder,
        {"template": "multi_branch/cross_location_reports.html"},
        name="multibranch_cross_location_reports",
    ),
    # System & Settings
    path("company-settings/", views.company_settings, name="company_settings"),
    path("user-management/", views.user_management, name="user_management"),
    path("integrations/", views.integrations, name="integrations"),
    path("backup-restore/", views.backup_restore, name="backup_restore"),
    # Network utilities
    path("sse/network/", views.network_sse, name="network_sse"),
    path("api/ping/", views.network_ping, name="network_ping"),
    path("api/client-ip/", views.client_ip, name="client_ip"),
    path("coming-soon/<str:feature>/", views.coming_soon, name="coming_soon"),
    path('locked/<str:feature>/', views.locked_page, name='locked_page'),

]
