from django import forms
from .models import (
    Category,
    Item,
    Customer,
    User,
    Sale,
    Discount,
    GiftCard,
    EmployeeProfile,
)
from django.utils.translation import gettext_lazy as _


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            "parent",
            "name_ar",
            "name_en",
            "description_ar",
            "description_en",
            "is_active",
        ]


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            "item_type",
            "category",
            "name_ar",
            "name_en",
            "description_ar",
            "description_en",
            "sku",
            "barcode",
            "cost_price",
            "selling_price",
            "stock_quantity",
            "min_stock",
            "image",
            "is_active",
        ]


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "first_name_ar",
            "last_name_ar",
            "first_name_en",
            "last_name_en",
            "phone",
            "email",
            "address",
            "loyalty_points",
            "notes",
        ]


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "role", "full_name_ar", "full_name_en", "phone"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["customer", "payment_method", "discount", "tax", "notes"]
        widgets = {
            "discount": forms.NumberInput(attrs={"step": "0.01"}),
            "tax": forms.NumberInput(attrs={"step": "0.01"}),
        }


class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = [
            "code",
            "description",
            "discount_type",
            "value",
            "valid_from",
            "valid_to",
            "usage_limit",
            "is_active",
        ]
        widgets = {
            "valid_from": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "valid_to": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class GiftCardForm(forms.ModelForm):
    class Meta:
        model = GiftCard
        fields = ["code", "initial_balance", "issued_to", "expires_at"]
        widgets = {
            "expires_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class EmployeeForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, label=_("First Name"))
    last_name = forms.CharField(max_length=150, label=_("Last Name"))
    email = forms.EmailField(label=_("Email"))
    phone = forms.CharField(max_length=20, required=False, label=_("Phone"))
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, label=_("Role"))
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label=_("Password"),
        help_text=_("Set a password for the new employee."),
    )

    class Meta:
        model = EmployeeProfile
        fields = ["hire_date", "commission_rate", "hourly_rate", "is_active"]
        widgets = {
            "hire_date": forms.DateInput(attrs={"type": "date"}),
            "commission_rate": forms.NumberInput(attrs={"step": "0.01"}),
            "hourly_rate": forms.NumberInput(attrs={"step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            user = self.instance.user
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email
            self.fields["phone"].initial = user.phone
            self.fields["role"].initial = user.role

    def save(self, commit=True):
        if self.instance.pk:
            user = self.instance.user
        else:
            user = User()

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data["phone"]
        user.role = self.cleaned_data["role"]
        if not user.username:
            user.username = self.cleaned_data["email"]
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()

        self.instance.user = user
        return super().save(commit=commit)
