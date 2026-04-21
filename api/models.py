from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    health_interests = models.JSONField(default=list, blank=True)
    preferred_specialty = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class Doctor(models.Model):
    AVAILABILITY_CHOICES = [
        ("available", "Available"),
        ("busy", "Busy"),
        ("unavailable", "Unavailable"),
    ]

    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    hospital = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    availability = models.CharField(
        max_length=20, choices=AVAILABILITY_CHOICES, default="available"
    )
    avatar = models.ImageField(upload_to="doctors/", blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    consultation_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.name} - {self.specialty}"

    @property
    def is_available(self):
        return self.availability == "available"


class Drug(models.Model):
    CATEGORY_CHOICES = [
        ("antibiotics", "Antibiotics"),
        ("analgesics", "Analgesics"),
        ("antimalaria", "Antimalaria"),
        ("vitamins", "Vitamins"),
        ("antihypertensive", "Antihypertensive"),
        ("antidiabetic", "Antidiabetic"),
        ("general", "General"),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(
        max_length=100, choices=CATEGORY_CHOICES, default="general"
    )
    description = models.TextField(blank=True)
    dosage = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to="drugs/", blank=True, null=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def is_available(self):
        return self.stock > 0


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.drug.name} x{self.quantity}"

    @property
    def total_price(self):
        return self.drug.price * self.quantity


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("rescheduled", "Rescheduled"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="appointments"
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="appointments"
    )
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    description = models.TextField(blank=True)
    reference_number = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Dr. {self.doctor.name} on {self.date}"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            import random
            import string

            self.reference_number = "PH-" + "".join(
                random.choices(string.ascii_uppercase + string.digits, k=6)
            )
        super().save(*args, **kwargs)


class MedicalTip(models.Model):
    CATEGORY_CHOICES = [
        ("general", "General Health"),
        ("nutrition", "Nutrition"),
        ("fitness", "Fitness"),
        ("mental_health", "Mental Health"),
        ("heart_health", "Heart Health"),
        ("diabetes", "Diabetes"),
        ("hygiene", "Hygiene"),
        ("sleep", "Sleep"),
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default="general"
    )
    icon = models.CharField(max_length=10, blank=True, default="💊")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
