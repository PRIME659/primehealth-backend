from django.contrib.auth.models import User
from rest_framework import serializers
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

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=["patient", "doctor", "pharmacist"], default="patient"
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password",
            "role",
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return data

    def create(self, validated_data):
        role = validated_data.pop("role", "patient")
        validated_data.pop("confirm_password", None)
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
        )
        UserProfile.objects.create(user=user, role=role)
        return user


class DoctorTimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorTimeSlot
        fields = ["id", "day", "start_time", "end_time", "is_available"]


class DoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = [
            "id",
            "license_number",
            "years_of_experience",
            "education",
            "certifications",
            "languages_spoken",
            "consultation_duration",
            "is_accepting_patients",
        ]


class DrugOrderSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    pharmacist_name = serializers.SerializerMethodField()

    class Meta:
        model = DrugOrder
        fields = [
            "id",
            "user",
            "user_name",
            "pharmacist",
            "pharmacist_name",
            "items",
            "total_amount",
            "status",
            "prescription_ref",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "pharmacist", "created_at", "updated_at"]

    def get_user_name(self, obj):
        return obj.user.get_full_name()

    def get_pharmacist_name(self, obj):
        if obj.pharmacist:
            return obj.pharmacist.get_full_name()
        return None


class ClinicalNoteSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    appointment_date = serializers.SerializerMethodField()

    class Meta:
        model = ClinicalNote
        fields = [
            "id",
            "appointment",
            "patient_name",
            "appointment_date",
            "diagnosis",
            "prescription",
            "notes",
            "follow_up_date",
            "created_at",
        ]

    def get_patient_name(self, obj):
        return obj.patient.get_full_name()

    def get_appointment_date(self, obj):
        return obj.appointment.date


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["phone", "blood_group", "health_interests", "preferred_specialty"]


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "profile"]


class DoctorSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = [
            "id",
            "name",
            "specialty",
            "hospital",
            "location",
            "bio",
            "rating",
            "availability",
            "is_available",
            "avatar",
            "avatar_url",
            "experience_years",
            "consultation_fee",
            "created_at",
        ]

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None


class DrugSerializer(serializers.ModelSerializer):
    is_available = serializers.BooleanField(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Drug
        fields = [
            "id",
            "name",
            "category",
            "description",
            "dosage",
            "price",
            "stock",
            "is_available",
            "image",
            "image_url",
            "manufacturer",
            "created_at",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class CartItemSerializer(serializers.ModelSerializer):
    drug = DrugSerializer(read_only=True)
    drug_id = serializers.IntegerField(write_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = CartItem
        fields = ["id", "drug", "drug_id", "quantity", "total_price", "added_at"]


class AppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    doctor_id = serializers.IntegerField(write_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "user",
            "doctor",
            "doctor_id",
            "date",
            "time",
            "status",
            "description",
            "reference_number",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["reference_number", "status", "created_at", "updated_at"]

    def validate_date(self, value):
        from django.utils import timezone

        if value < timezone.now().date():
            raise serializers.ValidationError("Appointment date cannot be in the past.")
        return value


class MedicalTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalTip
        fields = ["id", "title", "content", "category", "icon", "created_at"]
