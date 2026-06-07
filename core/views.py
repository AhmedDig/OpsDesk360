from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .decorators import role_required
from .models import Category, Item, Customer
from .forms import CategoryForm, ItemForm, CustomerForm, UserCreateForm

# Dashboard
@login_required
def dashboard(request):
    context = {
        'total_items': Item.objects.count(),
        'total_customers': Customer.objects.count(),
        'total_categories': Category.objects.count(),
        # later: recent sales, low stock, etc.
    }
    return render(request, 'core/dashboard.html', context)

# Category CRUD
@login_required
def category_list(request):
    categories = Category.objects.filter(is_active=True)
    paginator = Paginator(categories, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/category_list.html', {'page_obj': page_obj})

@login_required
@role_required(['dept_admin', 'super_admin'])
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'core/category_form.html', {'form': form, 'title': 'Create Category'})

@login_required
@role_required(['dept_admin', 'super_admin'])
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated.")
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'core/category_form.html', {'form': form, 'title': 'Edit Category'})

@login_required
@role_required(['dept_admin', 'super_admin'])
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category deleted.")
    return redirect('category_list')

# Item CRUD (similar pattern)
@login_required
def item_list(request):
    items = Item.objects.filter(is_active=True)
    paginator = Paginator(items, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/item_list.html', {'page_obj': page_obj})

@login_required
@role_required(['dept_admin', 'super_admin'])
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Item created.")
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'core/item_form.html', {'form': form, 'title': 'Create Item'})

@login_required
@role_required(['dept_admin', 'super_admin'])
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Item updated.")
            return redirect('item_list')
    else:
        form = ItemForm(instance=item)
    return render(request, 'core/item_form.html', {'form': form, 'title': 'Edit Item'})

@login_required
@role_required(['dept_admin', 'super_admin'])
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    item.delete()
    messages.success(request, "Item deleted.")
    return redirect('item_list')

# Customer CRUD
@login_required
def customer_list(request):
    customers = Customer.objects.all()
    paginator = Paginator(customers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'core/customer_list.html', {'page_obj': page_obj})

@login_required
@role_required(['dept_admin', 'moderator', 'super_admin'])
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer added.")
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'core/customer_form.html', {'form': form, 'title': 'Add Customer'})

@login_required
@role_required(['dept_admin', 'moderator', 'super_admin'])
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer updated.")
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'core/customer_form.html', {'form': form, 'title': 'Edit Customer'})

@login_required
@role_required(['dept_admin', 'super_admin'])
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    messages.success(request, "Customer deleted.")
    return redirect('customer_list')

# User management (for business admin)
@login_required
@role_required(['dept_admin', 'super_admin'])
def user_list(request):
    users = User.objects.all()
    return render(request, 'core/user_list.html', {'users': users})

@login_required
@role_required(['dept_admin', 'super_admin'])
def user_create(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created.")
            return redirect('user_list')
    else:
        form = UserCreateForm()
    return render(request, 'core/user_form.html', {'form': form, 'title': 'Create User'})