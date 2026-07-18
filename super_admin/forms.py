from django import forms
from .models import Business, PaymentRecord, Ticket


class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = [
            "client_domain",
            "status",
            "plan",
            "features",
            "limits",
            "payment_method",
            "trial_ends",
        ]
        widgets = {
            "features": forms.Textarea(attrs={"rows": 4, "class": "font-mono"}),
            "limits": forms.Textarea(attrs={"rows": 3, "class": "font-mono"}),
            "trial_ends": forms.DateInput(attrs={"type": "date"}),
        }


class FeatureToggleForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ["features"]
        widgets = {"features": forms.Textarea(attrs={"rows": 5, "class": "font-mono"})}


class PaymentForm(forms.ModelForm):
    class Meta:
        model = PaymentRecord
        fields = ["business", "amount", "method", "transaction_id", "notes"]


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["status", "time_spent", "resolution_notes"]
