from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from super_admin.models import Business
from .thread_local import get_current_business, get_current_user_is_superuser
from django.db.models import F
from django.conf import settings
from django.utils import timezone


class BusinessAwareManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        current_business = get_current_business()
        is_superuser = get_current_user_is_superuser()
        if current_business and not is_superuser:
            return qs.filter(business=current_business)
        return qs


class User(AbstractUser):
    ROLE_CHOICES = [
        ("super_admin", "Super Admin"),
        ("dept_admin", "Business Admin"),
        ("moderator", "Moderator"),
        ("agent", "Agent"),
        ("user", "User"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")
    full_name_ar = models.CharField(max_length=200, blank=True)
    full_name_en = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    language = models.CharField(
        max_length=5, choices=[("en", "English"), ("ar", "Arabic")], default="en"
    )
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return self.username


class Category(models.Model):
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    name_ar = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)
    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    objects = BusinessAwareManager()

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_en


class Item(models.Model):
    TYPE_CHOICES = [("product", "Product"), ("service", "Service")]
    item_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="product")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    name_ar = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)
    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    sku = models.CharField(max_length=100, unique=True)
    barcode = models.CharField(max_length=100, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    objects = BusinessAwareManager()
    stock_quantity = models.PositiveIntegerField(default=0)
    min_stock = models.PositiveIntegerField(default=0)  # low stock threshold
    image = models.ImageField(upload_to="items/", null=True, blank=True)

    def __str__(self):
        return self.name_en


class Customer(models.Model):
    first_name_ar = models.CharField(max_length=100)
    last_name_ar = models.CharField(max_length=100)
    first_name_en = models.CharField(max_length=100)
    last_name_en = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    loyalty_points = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    objects = BusinessAwareManager()

    def __str__(self):
        return f"{self.first_name_en} {self.last_name_en}"


class Sale(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("synced", "Synced"),
    ]
    sale_id = models.CharField(max_length=50, unique=True, blank=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="sales")
    sale_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="completed"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    objects = BusinessAwareManager()

    def save(self, *args, **kwargs):
        if not self.sale_id:

            today = timezone.now().strftime("%Y%m%d")
            last_sale = (
                Sale.objects.filter(sale_id__startswith=f"INV-{today}")
                .order_by("-sale_id")
                .first()
            )
            if last_sale:
                last_num = int(last_sale.sale_id.split("-")[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.sale_id = f"INV-{today}-{new_num:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.sale_id


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    allocation = models.ForeignKey(
        "InventoryAllocation", on_delete=models.SET_NULL, null=True, blank=True
    )
    objects = BusinessAwareManager()
    returned = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class InventoryAllocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="allocations")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    allocated_quantity = models.PositiveIntegerField(default=0)
    sold_quantity = models.PositiveIntegerField(default=0)
    remaining_quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    objects = BusinessAwareManager()

    class Meta:
        unique_together = ("user", "item")

    def save(self, *args, **kwargs):
        self.remaining_quantity = self.allocated_quantity - self.sold_quantity
        super().save(*args, **kwargs)


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]
    ticket_number = models.CharField(max_length=50, unique=True, blank=True)
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    items = models.ManyToManyField(Item, through="OrderItem")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )  # percentage (e.g., 16)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    objects = BusinessAwareManager()

    def save(self, *args, **kwargs):
        # Generate ticket number only if not already set (typically on creation)
        if not self.ticket_number:
            from django.utils import timezone

            today = timezone.now().strftime("%Y%m%d")
            last_order = (
                Order.objects.filter(ticket_number__startswith=f"ORD-{today}")
                .order_by("-ticket_number")
                .first()
            )
            if last_order:
                last_num = int(last_order.ticket_number.split("-")[-1])
                new_num = last_num + 1
            else:
                new_num = 1
            self.ticket_number = f"ORD-{today}-{new_num:04d}"

        # Correctly calculate final_amount (tax is a percentage)
        self.final_amount = (
            self.total_amount - self.discount + (self.total_amount * self.tax / 100)
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.ticket_number


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Discount(models.Model):
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(
        max_length=20,
        choices=[("percentage", "Percentage"), ("fixed", "Fixed Amount")],
        default="percentage",
    )
    value = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(default=1)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)


class GiftCard(models.Model):
    code = models.CharField(max_length=50, unique=True)
    initial_balance = models.DecimalField(max_digits=10, decimal_places=2)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2)
    issued_to = models.CharField(max_length=200, blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)


class Return(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    items = models.ManyToManyField(SaleItem)
    reason = models.TextField()
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(User, on_delete=models.PROTECT)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)


class EmployeeProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    hire_date = models.DateField(null=True, blank=True)
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        help_text="Commission percentage (e.g., 5.00 = 5%)"
    )
    hourly_rate = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.00
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_employees'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_employee_profile'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email}"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.email


class TimeLog(models.Model):
    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name='time_logs'
    )
    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'core_time_log'
        ordering = ['-clock_in']

    def __str__(self):
        return f"{self.employee.full_name} - {self.clock_in.strftime('%Y-%m-%d %H:%M')}"

    @property
    def duration(self):
        if self.clock_out:
            return self.clock_out - self.clock_in
        return None