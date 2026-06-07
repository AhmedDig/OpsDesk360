from django import forms
from .models import Category, Item, Customer, User

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['parent', 'name_ar', 'name_en', 'description_ar', 'description_en', 'is_active']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_type', 'category', 'name_ar', 'name_en', 'description_ar', 'description_en',
                  'sku', 'barcode', 'cost_price', 'selling_price', 'is_active']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name_ar', 'last_name_ar', 'first_name_en', 'last_name_en',
                  'phone', 'email', 'address', 'loyalty_points', 'notes']

class UserCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'full_name_ar', 'full_name_en', 'phone']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user