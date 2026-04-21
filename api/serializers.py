from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile
from .models import Doctor, Drug, CartItem, Appointment, MedicalTip


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password", "confirm_password"]

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
        validated_data.pop("confirm_password")
        user = User.objects.create_user(
            username=validated_data["email"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
        )
        UserProfile.objects.create(user=user)
        return user


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
