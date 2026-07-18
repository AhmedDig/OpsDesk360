import json
import time
from django.db.models import F, Sum, Count, Q
from django.utils import timezone
from decimal import Decimal
from .models import Order, OrderItem
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import (
    HttpResponse,
    JsonResponse,
    StreamingHttpResponse,
    HttpResponseForbidden,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .decorators import role_required
from .forms import CategoryForm, CustomerForm, ItemForm, UserCreateForm, EmployeeForm
from .models import (
    Category,
    Customer,
    EmployeeProfile,
    InventoryAllocation,
    Item,
    Order,
    OrderItem,
    Sale,
    SaleItem,
    User,
    EmployeeProfile,  # <-- add
    TimeLog,
)
from .utils import htmx_render
from django.utils.translation import gettext as _


# ==========================================
# 1. Authentication & Base Views
# ==========================================


def client_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        client_domain = request.POST.get("client_domain")
        user = authenticate(
            request, username=username, password=password, client_domain=client_domain
        )
        if user is not None:
            auth_login(request, user)
            return redirect("/")
        else:
            messages.error(request, "Invalid credentials or client domain")
    return htmx_render(request, "registration/login.html")


@login_required
def frame(request):
    return render(request, "base.html")


@login_required
def dashboard(request):
    business = request.user.business
    today = timezone.now().date()
    total_items = Item.objects.filter(business=business).count()
    total_customers = Customer.objects.filter(business=business).count()
    low_stock_items = Item.objects.filter(
        business=business,
        is_active=True,
        item_type="product",
        stock_quantity__lte=F("min_stock"),
    ).order_by("stock_quantity")[:10]
    low_stock_count = low_stock_items.count()
    today_sales = Sale.objects.filter(
        business=business, sale_date__date=today, status="completed"
    ).aggregate(total=Sum("final_amount"), count=Count("id"))
    # Create context dictionary first
    context = {
        "total_items": total_items,
        "total_customers": total_customers,
        "low_stock_count": low_stock_count,
        "low_stock_items": low_stock_items,
        "today_sales_total": today_sales["total"] or 0,
        "today_sales_count": today_sales["count"] or 0,
    }
    # Add top products and recent sales
    top_products = (
        SaleItem.objects.filter(sale__business=business, sale__sale_date__date=today)
        .values("item__name_en")
        .annotate(total_qty=Sum("quantity"))
        .order_by("-total_qty")[:5]
    )
    recent_sales = Sale.objects.filter(business=business).order_by("-sale_date")[:5]
    context.update(
        {
            "top_products": top_products,
            "recent_sales": recent_sales,
        }
    )
    return htmx_render(request, "partials/dashboard.html", context)


# ==========================================
# 2. Category Management (CRUD)
# ==========================================


@login_required
def category_list(request):
    categories = Category.objects.filter(is_active=True)
    paginator = Paginator(categories, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return htmx_render(
        request, "partials/core/category_list.html", {"page_obj": page_obj}
    )


@login_required
@role_required("dept_admin", "super_admin")
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.business = request.user.business
            category.save()
            messages.success(request, "Category created successfully.")
            return redirect("category_list")
    else:
        form = CategoryForm()
    return htmx_render(
        request,
        "partials/core/category_form.html",
        {"form": form, "title": "Create Category"},
    )


@login_required
@role_required("dept_admin", "super_admin")
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated.")
            return redirect("category_list")
    else:
        form = CategoryForm(instance=category)
    return htmx_render(
        request,
        "partials/core/category_form.html",
        {"form": form, "title": "Edit Category"},
    )


@login_required
@role_required("dept_admin", "super_admin")
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category deleted.")
    return redirect("category_list")


# ==========================================
# 3. Catalog (CRUD)
# ==========================================


from django.db.models import F, Q


@login_required
def catalog_list(request):
    products = Item.objects.filter(
        business=request.user.business, is_active=True, item_type="product"
    ).order_by("name_en")
    services = Item.objects.filter(
        business=request.user.business, is_active=True, item_type="service"
    ).order_by("name_en")
    # Add low stock flag for products
    for item in products:
        item.is_low_stock = item.stock_quantity <= item.min_stock
    context = {
        "products": products,
        "services": services,
    }
    return htmx_render(request, "partials/catalog/catalog_list.html", context)


@login_required
@role_required(
    "dept_admin",
    "super_admin",
    "inventory_manager",
    "staff",
    "receptionist",
    "cashier",
)
def catalog_create(request):
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.business = request.user.business
            item.save()
            messages.success(request, f"Item {item.name_en} created.")
            return redirect("catalog_list")
    else:
        form = ItemForm()
    return htmx_render(
        request,
        "partials/catalog/catalog_form.html",
        {"form": form, "title": "Create Item"},
    )


@login_required
@role_required("dept_admin", "super_admin")
def catalog_edit(request, pk):
    item = get_object_or_404(Item, pk=pk, business=request.user.business)
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"Item {item.name_en} updated.")
            return redirect("catalog_list")
    else:
        form = ItemForm(instance=item)
    return htmx_render(
        request,
        "partials/catalog/catalog_form.html",
        {"form": form, "title": "Edit Item"},
    )


@login_required
@role_required("dept_admin", "super_admin")
def catalog_delete(request, pk):
    item = get_object_or_404(Item, pk=pk, business=request.user.business)
    item.delete()
    messages.success(request, "Item deleted.")
    return redirect("catalog_list")


@login_required
@role_required("dept_admin", "super_admin")
def catalog_adjust_stock(request, pk):
    item = get_object_or_404(Item, pk=pk, business=request.user.business)
    if request.method == "POST":
        new_qty = int(request.POST.get("stock_quantity", 0))
        item.stock_quantity = new_qty
        item.save()
        messages.success(request, f"Stock updated for {item.name_en}")
        return redirect("catalog_list")
    return htmx_render(request, "partials/catalog/stock_adjust.html", {"item": item})


# ========== Reusable Product & Service Grids ==========
@login_required
def product_grid(request):
    items = Item.objects.filter(
        is_active=True,
        business=request.user.business,
        item_type="product",
    ).order_by("name_en")
    return render(request, "partials/pos/product_list.html", {"items": items})


@login_required
def service_grid(request):
    items = Item.objects.filter(
        is_active=True,
        business=request.user.business,
        item_type="service",
    ).order_by("name_en")
    return render(request, "partials/pos/service_list.html", {"items": items})


# ==========================================
# 4. Customer Management (CRUD & Search)
# ==========================================


@login_required
def customer_list(request):
    customers = Customer.objects.all()
    paginator = Paginator(customers, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return htmx_render(
        request, "partials/core/customer_list.html", {"page_obj": page_obj}
    )


@login_required
@role_required("dept_admin", "moderator", "super_admin")
def customer_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.business = request.user.business
            customer.save()
            messages.success(request, "Customer added.")
            return redirect("customer_list")
    else:
        form = CustomerForm()
    return htmx_render(
        request,
        "partials/core/customer_form.html",
        {"form": form, "title": "Add Customer"},
    )


@login_required
@role_required("dept_admin", "moderator", "super_admin")
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer updated.")
            return redirect("customer_list")
    else:
        form = CustomerForm(instance=customer)
    return htmx_render(
        request,
        "partials/core/customer_form.html",
        {"form": form, "title": "Edit Customer"},
    )


@login_required
@role_required("dept_admin", "super_admin")
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    messages.success(request, "Customer deleted.")
    return redirect("customer_list")


@login_required
def customer_search(request):
    query = request.GET.get("q", "")
    if len(query) < 2:
        return HttpResponse("")
    customers = Customer.objects.filter(
        Q(first_name_en__icontains=query)
        | Q(last_name_en__icontains=query)
        | Q(first_name_ar__icontains=query)
        | Q(last_name_ar__icontains=query)
        | Q(phone__icontains=query),
        business=request.user.business,
    )[:10]
    html = ""
    for c in customers:
        html += f'<div class="p-2 hover:bg-blue-100 cursor-pointer" hx-on:click="selectCustomer({c.id}, \'{c.first_name_en} {c.last_name_en}\')">{c.first_name_en} {c.last_name_en} - {c.phone}</div>'
    return HttpResponse(html)


# ==========================================
# 5. User Management
# ==========================================


@login_required
@role_required("dept_admin", "super_admin")
def user_list(request):
    users = User.objects.all()
    return htmx_render(request, "partials/core/user_list.html", {"users": users})


@login_required
@role_required("dept_admin", "super_admin")
def user_create(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.business = request.user.business
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "User created.")
            return redirect("user_list")
    else:
        form = UserCreateForm()
    return htmx_render(
        request, "partials/core/user_form.html", {"form": form, "title": "Create User"}
    )


# ==========================================
# 6. Point of Sale (POS) & Order Management
# ==========================================


# ---------- POS/Cart Helpers ----------
def render_cart_for_order(request, order):
    order_items = order.order_items.select_related("item")
    cart_items = []
    subtotal = Decimal("0")
    for oi in order_items:
        cart_items.append(
            {
                "id": oi.item.id,
                "name": (
                    oi.item.name_en
                    if request.LANGUAGE_CODE == "en"
                    else oi.item.name_ar
                ),
                "quantity": oi.quantity,
                "unit_price": float(oi.unit_price),
                "total": float(oi.total_price),
            }
        )
        subtotal += oi.total_price
    order.total_amount = subtotal
    order.final_amount = subtotal - order.discount + (subtotal * order.tax / 100)
    order.save(update_fields=["total_amount", "final_amount", "discount", "tax"])
    return render(
        request,
        "partials/pos/cart_partial.html",
        {
            "cart_items": cart_items,
            "subtotal": float(subtotal),
            "order": order,
            "customers": Customer.objects.all(),
        },
    )


def render_product_grid(request):
    items = Item.objects.filter(
        is_active=True,
        business=request.user.business,
        item_type__in=["product", "service"],
    ).order_by("name_en")
    return render(request, "partials/pos/product_grid.html", {"items": items})


# ---------- POS/Order Views ----------


@login_required
def pos_home(request):
    # Do NOT automatically create an order – only keep existing session order
    active_id = request.session.get("active_order_id")
    if (
        active_id
        and Order.objects.filter(
            id=active_id, user=request.user, status="pending"
        ).exists()
    ):
        pass
    else:
        request.session.pop("active_order_id", None)

    products = Item.objects.filter(
        is_active=True, business=request.user.business, item_type="product"
    ).order_by("name_en")
    services = Item.objects.filter(
        is_active=True, business=request.user.business, item_type="service"
    ).order_by("name_en")
    context = {"products": products, "services": services}
    return htmx_render(request, "partials/pos/pos.html", context)


@login_required
def active_orders_list(request):
    if not request.user.business:
        return render(request, "partials/pos/active_orders.html", {"orders": []})
    orders = Order.objects.filter(
        user=request.user, status="pending", business=request.user.business
    ).order_by("created_at")
    return render(request, "partials/pos/active_orders.html", {"orders": orders})


@login_required
def create_order(request):
    order = Order.objects.create(
        user=request.user, business=request.user.business, tax=16
    )
    request.session["active_order_id"] = order.id
    orders = Order.objects.filter(
        user=request.user, status="pending", business=request.user.business
    ).order_by("created_at")
    return render(request, "partials/pos/active_orders.html", {"orders": orders})


@login_required
def switch_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        status="pending",
        business=request.user.business,
    )
    request.session["active_order_id"] = order.id
    return render_cart_for_order(request, order)


@login_required
def delete_order(request, order_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        status="pending",
        business=request.user.business,
    )
    for oi in order.order_items.select_related("item"):
        if oi.item.item_type == "product":
            oi.item.stock_quantity += oi.quantity
            oi.item.save()
    order.delete()
    if request.session.get("active_order_id") == order.id:
        request.session.pop("active_order_id", None)
    return JsonResponse({"success": True})


@login_required
def update_order_customer(request, order_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        status="pending",
        business=request.user.business,
    )
    customer_id = request.POST.get("customer_id")
    if customer_id:
        try:
            customer = Customer.objects.get(
                id=customer_id, business=request.user.business
            )
            order.customer = customer
        except Customer.DoesNotExist:
            order.customer = None
    else:
        order.customer = None
    order.save()
    return render_cart_for_order(request, order)


@login_required
def update_order_note(request, order_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        status="pending",
        business=request.user.business,
    )
    order.notes = request.POST.get("note", "")
    order.save()
    return render_cart_for_order(request, order)


@login_required
def split_order(request, order_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        status="pending",
        business=request.user.business,
    )
    item_ids = request.POST.getlist("item_ids")
    if not item_ids:
        return JsonResponse({"error": "No items selected"}, status=400)
    new_order = Order.objects.create(
        user=request.user, business=request.user.business, tax=16
    )
    moved_items = order.order_items.filter(item_id__in=item_ids)
    for oi in moved_items:
        oi.order = new_order
        oi.save()
    order.save()
    new_order.save()
    return render_cart_for_order(request, order)


@login_required
def update_order_discount(request, order_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    order = get_object_or_404(Order, id=order_id, user=request.user, status="pending")
    discount = Decimal(request.POST.get("discount", 0))
    order.discount = discount
    order.save()
    return render_cart_for_order(request, order)


@login_required
def update_order_tax(request, order_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    order = get_object_or_404(Order, id=order_id, user=request.user, status="pending")
    tax = Decimal(request.POST.get("tax", 0))
    order.tax = tax
    order.save()
    return render_cart_for_order(request, order)


@login_required
@require_http_methods(["POST"])
def add_to_cart(request):
    item_id = request.POST.get("item_id")
    if not item_id:
        return JsonResponse({"error": "Item ID required"}, status=400)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except ValueError:
        quantity = 1

    item = get_object_or_404(Item, id=item_id, business=request.user.business)

    if item.item_type == "product":
        if item.stock_quantity < quantity:
            return JsonResponse(
                {"error": f"Not enough stock. Available: {item.stock_quantity}"},
                status=400,
            )
        item.stock_quantity -= quantity
        item.save()

    order_id = request.session.get("active_order_id")
    if not order_id:
        order = Order.objects.create(
            user=request.user, business=request.user.business, tax=16
        )
        request.session["active_order_id"] = order.id
    else:
        order = get_object_or_404(
            Order,
            id=order_id,
            user=request.user,
            status="pending",
            business=request.user.business,
        )

    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        item=item,
        defaults={"unit_price": item.selling_price, "quantity": 0},
    )
    order_item.quantity += quantity
    order_item.save()

    # Render cart only – product grid will be refreshed by frontend
    cart_html = render_cart_for_order(request, order).content.decode("utf-8")
    return HttpResponse(cart_html)


@login_required
def update_cart_item(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    order_id = request.session.get("active_order_id")
    if not order_id:
        return JsonResponse({"error": "No active order"}, status=400)

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        status="pending",
        business=request.user.business,
    )
    item_id = request.POST.get("item_id")
    new_quantity = int(request.POST.get("quantity", 0))
    order_item = get_object_or_404(OrderItem, order=order, item_id=item_id)
    item = order_item.item
    old_quantity = order_item.quantity
    diff = new_quantity - old_quantity

    if item.item_type == "product":
        if diff > 0:
            if item.stock_quantity < diff:
                new_quantity = old_quantity + item.stock_quantity
                diff = item.stock_quantity
                request.toast_message = (
                    f"Maximum stock available: {item.stock_quantity}"
                )
            item.stock_quantity -= diff
            item.save()
        elif diff < 0:
            item.stock_quantity += abs(diff)
            item.save()

    if new_quantity <= 0:
        order_item.delete()
    else:
        order_item.quantity = new_quantity
        order_item.save()

    cart_html = render_cart_for_order(request, order).content.decode("utf-8")
    response = HttpResponse(cart_html)
    if hasattr(request, "toast_message"):
        response["X-Toast-Message"] = request.toast_message
    return response


@login_required
def remove_cart_item(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    order_id = request.session.get("active_order_id")
    if not order_id:
        return JsonResponse({"error": "No active order"}, status=400)

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        status="pending",
        business=request.user.business,
    )
    item_id = request.POST.get("item_id")
    order_item = get_object_or_404(OrderItem, order=order, item_id=item_id)
    item = order_item.item

    if item.item_type == "product":
        item.stock_quantity += order_item.quantity
        item.save()

    order_item.delete()
    cart_html = render_cart_for_order(request, order).content.decode("utf-8")
    return HttpResponse(cart_html)


@login_required
def clear_cart(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    order_id = request.session.get("active_order_id")
    if not order_id:
        return JsonResponse({"error": "No active order"}, status=400)

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
        status="pending",
        business=request.user.business,
    )
    for oi in order.order_items.select_related("item"):
        if oi.item.item_type == "product":
            oi.item.stock_quantity += oi.quantity
            oi.item.save()
    order.order_items.all().delete()
    cart_html = render_cart_for_order(request, order).content.decode("utf-8")
    return HttpResponse(cart_html)


@login_required
def checkout(request):
    print("Checkout view called")
    order_id = request.session.get("active_order_id")
    if not order_id:
        return JsonResponse({"error": "No active order"}, status=400)
    order = get_object_or_404(Order, id=order_id, user=request.user, status="pending")
    if order.order_items.count() == 0:
        messages.error(request, "Order is empty.")
        return redirect("pos_home")

    customer_id = request.POST.get("customer")
    payment_method = request.POST.get("payment_method", "cash")
    discount = Decimal(request.POST.get("discount", 0))
    tax_percent = Decimal(request.POST.get("tax", 0))

    with transaction.atomic():
        # Calculate subtotal
        total_before = Decimal("0")
        for oi in order.order_items.all():
            if oi.item.item_type == "product":
                # Double-check stock (already deducted in add_to_cart, but prevent negative)
                if oi.item.stock_quantity < oi.quantity:
                    raise ValueError(f"Insufficient stock for {oi.item.name_en}")
                oi.item.stock_quantity -= oi.quantity
                oi.item.save()
            total_before += oi.unit_price * oi.quantity

        # Calculate final amount with percentage tax
        final_amount = total_before - discount + (total_before * tax_percent / 100)

        sale = Sale.objects.create(
            customer_id=customer_id if customer_id else None,
            user=request.user,
            discount=discount,
            tax=tax_percent,
            payment_method=payment_method,
            status="completed",
            business=request.user.business,
            total_amount=total_before,
            final_amount=final_amount,
        )

        for oi in order.order_items.all():
            SaleItem.objects.create(
                sale=sale,
                item=oi.item,
                quantity=oi.quantity,
                unit_price=oi.unit_price,
                total_price=oi.unit_price * oi.quantity,
            )

        order.status = "completed"
        order.save()
        request.session.pop("active_order_id", None)

    messages.success(request, f"Sale completed. Receipt #{sale.sale_id}")
    return redirect("pos_receipt", sale_id=sale.id)


@login_required
def pos_receipt(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    return htmx_render(request, "partials/pos/receipt.html", {"sale": sale})


@login_required
@require_http_methods(["POST"])
def sync_offline_sales(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    offline_sales = data.get("sales", [])
    results = []
    for offline_sale in offline_sales:
        try:
            with transaction.atomic():
                sale = Sale.objects.create(
                    customer_id=offline_sale.get("customer_id"),
                    user=request.user,
                    payment_method=offline_sale.get("payment_method", "cash"),
                    status="synced",
                    notes=f"Synced from offline queue at {timezone.now()}",
                    business=request.user.business,
                )
                total_before = Decimal("0")
                for item_data in offline_sale.get("items", []):
                    item = Item.objects.get(id=item_data["item_id"])
                    unit_price = item.selling_price
                    qty = Decimal(item_data["quantity"])
                    total_price = unit_price * qty
                    SaleItem.objects.create(
                        sale=sale,
                        item=item,
                        quantity=qty,
                        unit_price=unit_price,
                        total_price=total_price,
                    )
                    total_before += total_price
                sale.total_amount = total_before
                sale.final_amount = (
                    total_before
                    - Decimal(offline_sale.get("discount", 0))
                    + Decimal(offline_sale.get("tax", 0))
                )
                sale.save()
                results.append({"sale_id": sale.sale_id, "status": "success"})
        except Exception as e:
            results.append({"error": str(e), "status": "failed"})
    return JsonResponse({"results": results})


# ==========================================
# 7. sales
# ==========================================
# ==========================================
# Sales Management
# ==========================================


@login_required
def sales_list(request):
    sales = Sale.objects.filter(business=request.user.business).order_by("-sale_date")
    paginator = Paginator(sales, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return htmx_render(request, "partials/sales/invoices.html", {"page_obj": page_obj})


@login_required
def sale_detail(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id, business=request.user.business)
    return htmx_render(request, "partials/sales/sale_detail.html", {"sale": sale})


@login_required
def return_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id, business=request.user.business)
    if request.method == "POST":
        # Mark items as returned (simplified – create Return record)
        # Restock items (for products)
        items_to_return = request.POST.getlist("items")
        refund_amount = Decimal("0")
        for item_id in items_to_return:
            sale_item = get_object_or_404(SaleItem, id=item_id, sale=sale)
            if sale_item.item.item_type == "product":
                sale_item.item.stock_quantity += sale_item.quantity
                sale_item.item.save()
            refund_amount += sale_item.total_price
            sale_item.returned = True  # you need to add a 'returned' field to SaleItem
        # Create Return record
        Return.objects.create(
            sale=sale,
            reason=request.POST.get("reason", ""),
            refund_amount=refund_amount,
            processed_by=request.user,
            business=request.user.business,
        )
        messages.success(request, f"Return processed. Refund amount: {refund_amount}")
        return redirect("sales_list")
    return htmx_render(request, "partials/sales/return_form.html", {"sale": sale})


@login_required
def discounts_list(request):
    discounts = Discount.objects.filter(business=request.user.business).order_by(
        "-created_at"
    )
    return htmx_render(
        request, "partials/sales/discounts.html", {"discounts": discounts}
    )


@login_required
def discount_create(request):
    if request.method == "POST":
        form = DiscountForm(request.POST)
        if form.is_valid():
            discount = form.save(commit=False)
            discount.business = request.user.business
            discount.save()
            messages.success(request, "Discount created")
            return redirect("discounts_list")
    else:
        form = DiscountForm()
    return htmx_render(
        request,
        "partials/sales/discount_form.html",
        {"form": form, "title": "Create Discount"},
    )


# Similar for edit/delete


@login_required
def gift_cards_list(request):
    cards = GiftCard.objects.filter(business=request.user.business).order_by(
        "-issued_at"
    )
    return htmx_render(request, "partials/sales/gift_cards.html", {"cards": cards})


@login_required
def gift_card_create(request):
    if request.method == "POST":
        form = GiftCardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.business = request.user.business
            card.current_balance = card.initial_balance
            card.save()
            messages.success(request, "Gift card created")
            return redirect("gift_cards_list")
    else:
        form = GiftCardForm()
    return htmx_render(
        request,
        "partials/sales/gift_card_form.html",
        {"form": form, "title": "Create Gift Card"},
    )


# Discount edit, delete
@login_required
def discount_edit(request, pk):
    discount = get_object_or_404(Discount, pk=pk, business=request.user.business)
    if request.method == "POST":
        form = DiscountForm(request.POST, instance=discount)
        if form.is_valid():
            form.save()
            messages.success(request, "Discount updated")
            return redirect("discounts_list")
    else:
        form = DiscountForm(instance=discount)
    return htmx_render(
        request,
        "partials/sales/discount_form.html",
        {"form": form, "title": "Edit Discount"},
    )


@login_required
def discount_delete(request, pk):
    discount = get_object_or_404(Discount, pk=pk, business=request.user.business)
    discount.delete()
    messages.success(request, "Discount deleted")
    return redirect("discounts_list")


# Gift card redeem, delete
@login_required
def gift_card_redeem(request, pk):
    card = get_object_or_404(GiftCard, pk=pk, business=request.user.business)
    if request.method == "POST":
        amount = Decimal(request.POST.get("amount", 0))
        if amount <= 0 or amount > card.current_balance:
            messages.error(request, "Invalid amount")
            return redirect("gift_cards_list")
        card.current_balance -= amount
        card.save()
        messages.success(
            request, f"{amount} ₪ redeemed. Remaining: {card.current_balance} ₪"
        )
        return redirect("gift_cards_list")
    return htmx_render(request, "partials/sales/gift_card_redeem.html", {"card": card})


@login_required
def gift_card_delete(request, pk):
    card = get_object_or_404(GiftCard, pk=pk, business=request.user.business)
    card.delete()
    messages.success(request, "Gift card deleted")
    return redirect("gift_cards_list")


# ==========================================
# Employee Management (form‑based, consistent)
# ==========================================


def get_employee_profile(user):
    try:
        return user.employee_profile
    except EmployeeProfile.DoesNotExist:
        return None


@login_required
@role_required("dept_admin", "super_admin")
def employee_list(request):
    business = request.user.business
    employees = EmployeeProfile.objects.filter(
        user__business=business, is_active=True
    ).select_related("user")

    q = request.GET.get("q", "")
    if q:
        employees = employees.filter(
            Q(user__email__icontains=q)
            | Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
        )

    paginator = Paginator(employees, 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "q": q,
    }
    return htmx_render(request, "partials/employees/list.html", context)


@login_required
@role_required("dept_admin", "super_admin")
def employee_create(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            # Check if a user with this email already exists (globally)
            if User.objects.filter(email=email).exists():
                form.add_error("email", _("A user with this email already exists."))
                return htmx_render(
                    request,
                    "partials/employees/form.html",
                    {"form": form, "title": _("Add Employee")},
                )

            # Ensure password is provided for new user
            password = form.cleaned_data.get("password")
            if not password:
                form.add_error("password", _("Password is required for new employees."))
                return htmx_render(
                    request,
                    "partials/employees/form.html",
                    {"form": form, "title": _("Add Employee")},
                )

            profile = form.save(commit=False)
            # Set business on the user
            profile.user.business = request.user.business
            profile.user.save()
            profile.created_by = request.user
            profile.save()
            messages.success(request, _("Employee created successfully."))
            return redirect("employee_list")
    else:
        form = EmployeeForm()
    return htmx_render(
        request,
        "partials/employees/form.html",
        {"form": form, "title": _("Add Employee")},
    )


@login_required
@role_required("dept_admin", "super_admin")
def employee_edit(request, pk):
    profile = get_object_or_404(
        EmployeeProfile, pk=pk, user__business=request.user.business
    )
    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _("Employee updated."))
            return redirect("employee_list")
    else:
        form = EmployeeForm(instance=profile)
    return htmx_render(
        request,
        "partials/employees/form.html",
        {"form": form, "title": _("Edit Employee")},
    )


@login_required
@role_required("dept_admin", "super_admin")
def employee_delete(request, pk):
    profile = get_object_or_404(
        EmployeeProfile, pk=pk, user__business=request.user.business
    )
    if request.method == "POST":
        profile.is_active = False
        profile.user.is_active = False
        profile.user.save()
        profile.save()
        messages.success(request, _("Employee deactivated."))
        return redirect("employee_list")
    context = {"profile": profile}
    return htmx_render(request, "partials/employees/delete_confirm.html", context)


@login_required
def employee_detail(request, pk):
    profile = get_object_or_404(
        EmployeeProfile, pk=pk, user__business=request.user.business
    )
    user = profile.user
    is_self = request.user == user
    can_manage = request.user.role in ["dept_admin", "super_admin"]
    if not (is_self or can_manage):
        return HttpResponseForbidden("You don't have permission.")

    sales = Sale.objects.filter(user=user, business=request.user.business)
    total_sales = sales.aggregate(total=Sum("total_amount"))["total"] or Decimal("0.00")
    total_commission = total_sales * (profile.commission_rate / Decimal("100"))

    time_logs = profile.time_logs.filter(
        clock_in__gte=timezone.now() - timezone.timedelta(days=30)
    ).order_by("-clock_in")

    context = {
        "profile": profile,
        "user": user,
        "total_sales": total_sales,
        "total_commission": total_commission,
        "time_logs": time_logs,
        "can_manage": can_manage,
        "is_self": is_self,
    }
    return htmx_render(request, "partials/employees/detail.html", context)


@login_required
def employee_clock(request):
    profile = get_employee_profile(request.user)
    if not profile:
        return JsonResponse({"error": "No employee profile"}, status=400)

    open_log = profile.time_logs.filter(clock_out__isnull=True).first()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "in" and not open_log:
            TimeLog.objects.create(employee=profile, clock_in=timezone.now())
            return JsonResponse({"status": "clocked_in"})
        elif action == "out" and open_log:
            open_log.clock_out = timezone.now()
            open_log.save()
            return JsonResponse({"status": "clocked_out"})
        return JsonResponse({"error": "Invalid action"}, status=400)

    return JsonResponse(
        {
            "clocked_in": bool(open_log),
            "since": open_log.clock_in.isoformat() if open_log else None,
        }
    )


# ==========================================
# 8. System & Placeholders
# ==========================================


def placeholder(request, template):
    return htmx_render(request, f"partials/{template}", {})


def inventory_home(request):
    return htmx_render(request, "partials/inventory/stock_levels.html", {})


def sales_home(request):
    return htmx_render(request, "partials/sales/invoices.html", {})


def company_settings(request):
    return htmx_render(request, "partials/system/company_settings.html", {})


def integrations_home(request):
    return htmx_render(request, "partials/system/integrations.html", {})


def backup_restore(request):
    return htmx_render(request, "partials/system/backup_restore.html", {})


# ==========================================
# 9. Network Utilities
# ==========================================


def event_stream():
    while True:
        data = f"data: {time.time() * 1000}\n\n"
        yield data.encode("utf-8")
        time.sleep(5)


@csrf_exempt
def network_sse(request):
    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


def network_ping(request):
    return JsonResponse(
        {
            "status": "ok",
            "server_time": timezone.now().isoformat(),
        }
    )


def client_ip(request):
    from ipware import get_client_ip

    ip, _ = get_client_ip(request)
    if ip is None:
        ip = "0.0.0.0"
    return JsonResponse({"ip": ip})
