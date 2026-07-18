from django.db import models


class Business(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("suspended", "Suspended"),
        ("trial", "Trial"),
        ("deleted", "Deleted"),
    ]
    client_domain = models.CharField(max_length=100, unique=True)
    database_name = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="trial")
    trial_ends = models.DateField(null=True, blank=True)
    plan = models.CharField(max_length=20, default="basic")
    features = models.JSONField(default=dict)
    limits = models.JSONField(default=dict)
    payment_method = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.client_domain


class PaymentRecord(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business.client_domain} - {self.amount}"


class Ticket(models.Model):
    CATEGORY_CHOICES = [
        ("technical", "Technical"),
        ("billing", "Billing"),
        ("feature", "Feature Request"),
        ("other", "Other"),
    ]
    URGENCY_CHOICES = [
        ("low", "Low"),
        ("normal", "Normal"),
        ("high", "High"),
        ("critical", "Critical"),
    ]
    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default="other"
    )
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default="normal")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    resolution_notes = models.TextField(blank=True)
    time_spent = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
