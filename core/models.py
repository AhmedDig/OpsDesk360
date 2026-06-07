from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('dept_admin', 'Business Admin'),
        ('moderator', 'Moderator'),
        ('agent', 'Agent'),
        ('user', 'User'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    full_name_ar = models.CharField(max_length=200, blank=True)
    full_name_en = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    language = models.CharField(max_length=5, choices=[('en', 'English'), ('ar', 'Arabic')], default='en')

    def __str__(self):
        return self.username

class Category(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    name_ar = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)
    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_en

class Item(models.Model):
    TYPE_CHOICES = [('product', 'Product'), ('service', 'Service')]
    item_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='product')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
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

    def __str__(self):
        return f"{self.first_name_en} {self.last_name_en}"