from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import (
    UserProfile,
    Doctor,
    Drug,
    CartItem,
    Appointment,
    MedicalTip,
    DoctorProfile,
    DoctorTimeSlot,
    ClinicalNote,
    DrugOrder,
)

# ── Inline for UserProfile inside User ────────────────────────
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fields = ["phone", "blood_group", "health_interests", "preferred_specialty"]


# ── Extend the default User admin ─────────────────────────────
class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ["email", "first_name", "last_name", "is_active", "date_joined"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-date_joined"]


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ── UserProfile Admin ──────────────────────────────────────────
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "phone", "blood_group", "created_at"]
    search_fields = ["user__email", "user__first_name"]


# ── Doctor Admin ───────────────────────────────────────────────
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "specialty",
        "hospital",
        "rating",
        "availability",
        "experience_years",
        "consultation_fee",
    ]
    search_fields = ["name", "specialty", "hospital", "location"]
    list_filter = ["specialty", "availability"]
    list_editable = ["availability", "rating"]
    fieldsets = (
        (
            "Basic Info",
            {"fields": ("name", "specialty", "hospital", "location", "avatar")},
        ),
        ("Details", {"fields": ("bio", "experience_years", "consultation_fee")}),
        ("Status", {"fields": ("rating", "availability")}),
    )


# ── Drug Admin ─────────────────────────────────────────────────
@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "price",
        "stock",
        "is_available",
        "manufacturer",
    ]
    search_fields = ["name", "category", "manufacturer"]
    list_filter = ["category"]
    list_editable = ["price", "stock"]
    fieldsets = (
        ("Basic Info", {"fields": ("name", "category", "manufacturer", "image")}),
        ("Medical Info", {"fields": ("description", "dosage")}),
        ("Pricing & Stock", {"fields": ("price", "stock")}),
    )


@admin.register(DrugOrder)
class DrugOrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "total_amount", "status", "created_at"]
    search_fields = ["user__email", "prescription_ref"]
    list_filter = ["status"]
    list_editable = ["status"]


# ── CartItem Admin ─────────────────────────────────────────────
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["user", "drug", "quantity", "total_price", "added_at"]
    search_fields = ["user__email", "drug__name"]
    readonly_fields = ["total_price", "added_at"]


# ── Appointment Admin ──────────────────────────────────────────
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        "reference_number",
        "user",
        "doctor",
        "date",
        "time",
        "status",
        "created_at",
    ]
    search_fields = ["user__email", "doctor__name", "reference_number"]
    list_filter = ["status", "date"]
    list_editable = ["status"]
    readonly_fields = ["reference_number", "created_at", "updated_at"]
    fieldsets = (
        (
            "Appointment Info",
            {"fields": ("user", "doctor", "date", "time", "description")},
        ),
        ("Status", {"fields": ("status", "reference_number")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


# ── MedicalTip Admin ───────────────────────────────────────────
@admin.register(MedicalTip)
class MedicalTipAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "icon", "is_active", "created_at"]
    search_fields = ["title", "content"]
    list_filter = ["category", "is_active"]
    list_editable = ["is_active"]


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "doctor", "license_number", "is_accepting_patients"]
    search_fields = ["user__email", "doctor__name", "license_number"]


@admin.register(DoctorTimeSlot)
class DoctorTimeSlotAdmin(admin.ModelAdmin):
    list_display = ["doctor", "day", "start_time", "end_time", "is_available"]
    list_filter = ["day", "is_available"]
    search_fields = ["doctor__name"]


@admin.register(ClinicalNote)
class ClinicalNoteAdmin(admin.ModelAdmin):
    list_display = ["doctor", "patient", "appointment", "follow_up_date", "created_at"]
    search_fields = ["doctor__name", "patient__email"]


# ── Admin Site Customization ───────────────────────────────────
admin.site.site_header = "PrimeHealth Administration"
admin.site.site_title = "PrimeHealth Admin"
admin.site.index_title = "Welcome to PrimeHealth Admin Panel"
