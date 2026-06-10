from django.contrib.auth.models import User
from django.db import models as django_models
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import (
    IsDoctor,
    IsAdmin,
    IsDoctorOrAdmin,
    IsPharmacist,
    IsPharmacistOrAdmin,
)

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    UserProfileSerializer,
    DoctorSerializer,
    DrugSerializer,
    CartItemSerializer,
    AppointmentSerializer,
    MedicalTipSerializer,
    DoctorProfileSerializer,
    DoctorTimeSlotSerializer,
    ClinicalNoteSerializer,
    DrugOrderSerializer,
)
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
import random
import uuid


def get_tokens_for_user(user, session_id):
    refresh = RefreshToken.for_user(user)
    refresh["session_id"] = session_id
    refresh["role"] = user.profile.role
    refresh["full_name"] = f"{user.first_name} {user.last_name}"
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


# ── Admin Dashboard Overview ───────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_dashboard(request):
    from django.utils import timezone

    today = timezone.now().date()

    total_users = User.objects.filter(profile__role="patient").count()
    total_doctors = Doctor.objects.count()
    total_appointments = Appointment.objects.count()
    today_appointments = Appointment.objects.filter(date=today).count()
    total_drugs = Drug.objects.count()
    pending_appointments = Appointment.objects.filter(status="pending").count()
    completed_appointments = Appointment.objects.filter(status="completed").count()
    cancelled_appointments = Appointment.objects.filter(status="cancelled").count()

    recent_appointments = Appointment.objects.order_by("-created_at")[:10]
    recent_users = User.objects.filter(profile__role="patient").order_by(
        "-date_joined"
    )[:5]

    return Response(
        {
            "stats": {
                "total_users": total_users,
                "total_doctors": total_doctors,
                "total_appointments": total_appointments,
                "today_appointments": today_appointments,
                "total_drugs": total_drugs,
                "pending_appointments": pending_appointments,
                "completed_appointments": completed_appointments,
                "cancelled_appointments": cancelled_appointments,
            },
            "recent_appointments": AppointmentSerializer(
                recent_appointments, many=True
            ).data,
            "recent_users": UserSerializer(recent_users, many=True).data,
        }
    )


# ── Admin User Management ──────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_list(request):
    users = User.objects.all().order_by("-date_joined")

    search = request.query_params.get("search")
    if search:
        users = users.filter(
            django_models.Q(email__icontains=search)
            | django_models.Q(first_name__icontains=search)
            | django_models.Q(last_name__icontains=search)
        )

    role = request.query_params.get("role")
    if role:
        users = users.filter(profile__role=role)

    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_toggle_user(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    user.is_active = not user.is_active
    user.save()

    return Response(
        {
            "message": f"User {'activated' if user.is_active else 'deactivated'} successfully.",
            "is_active": user.is_active,
        }
    )


# ── Admin Doctor Management ────────────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_create_doctor(request):
    serializer = DoctorSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "message": "Doctor created successfully.",
                "doctor": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_update_doctor(request, pk):
    try:
        doctor = Doctor.objects.get(pk=pk)
    except Doctor.DoesNotExist:
        return Response(
            {"error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = DoctorSerializer(
        doctor, data=request.data, partial=True, context={"request": request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "message": "Doctor updated successfully.",
                "doctor": serializer.data,
            }
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_delete_doctor(request, pk):
    try:
        doctor = Doctor.objects.get(pk=pk)
        doctor.delete()
        return Response({"message": "Doctor deleted successfully."})
    except Doctor.DoesNotExist:
        return Response(
            {"error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND
        )


# ── Admin Appointment Management ───────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_appointment_list(request):
    appointments = Appointment.objects.all().order_by("-created_at")

    status_filter = request.query_params.get("status")
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    date_filter = request.query_params.get("date")
    if date_filter:
        appointments = appointments.filter(date=date_filter)

    doctor_filter = request.query_params.get("doctor")
    if doctor_filter:
        appointments = appointments.filter(doctor__id=doctor_filter)

    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_update_appointment(request, pk):
    try:
        appointment = Appointment.objects.get(pk=pk)
    except Appointment.DoesNotExist:
        return Response(
            {"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND
        )

    new_status = request.data.get("status")
    if new_status:
        appointment.status = new_status
        appointment.save()

    serializer = AppointmentSerializer(appointment)
    return Response(
        {
            "message": "Appointment updated successfully.",
            "appointment": serializer.data,
        }
    )


# ── Admin Drug Management ──────────────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_create_drug(request):
    serializer = DrugSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "message": "Drug created successfully.",
                "drug": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_update_drug(request, pk):
    try:
        drug = Drug.objects.get(pk=pk)
    except Drug.DoesNotExist:
        return Response({"error": "Drug not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = DrugSerializer(
        drug, data=request.data, partial=True, context={"request": request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "message": "Drug updated successfully.",
                "drug": serializer.data,
            }
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_delete_drug(request, pk):
    try:
        drug = Drug.objects.get(pk=pk)
        drug.delete()
        return Response({"message": "Drug deleted successfully."})
    except Drug.DoesNotExist:
        return Response({"error": "Drug not found."}, status=status.HTTP_404_NOT_FOUND)


# ── Admin Analytics ────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_analytics(request):
    from django.utils import timezone
    from datetime import timedelta

    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)

    appointments_last_7 = Appointment.objects.filter(
        created_at__date__gte=last_7_days
    ).count()

    appointments_last_30 = Appointment.objects.filter(
        created_at__date__gte=last_30_days
    ).count()

    new_users_last_7 = User.objects.filter(
        date_joined__date__gte=last_7_days, profile__role="patient"
    ).count()

    new_users_last_30 = User.objects.filter(
        date_joined__date__gte=last_30_days, profile__role="patient"
    ).count()

    appointments_by_status = {
        "pending": Appointment.objects.filter(status="pending").count(),
        "confirmed": Appointment.objects.filter(status="confirmed").count(),
        "completed": Appointment.objects.filter(status="completed").count(),
        "cancelled": Appointment.objects.filter(status="cancelled").count(),
        "rescheduled": Appointment.objects.filter(status="rescheduled").count(),
    }

    top_doctors = Doctor.objects.annotate(
        appointment_count=django_models.Count("appointments")
    ).order_by("-appointment_count")[:5]

    low_stock_drugs = Drug.objects.filter(stock__lte=10).order_by("stock")

    return Response(
        {
            "appointments": {
                "last_7_days": appointments_last_7,
                "last_30_days": appointments_last_30,
                "by_status": appointments_by_status,
            },
            "users": {
                "new_last_7_days": new_users_last_7,
                "new_last_30_days": new_users_last_30,
            },
            "top_doctors": DoctorSerializer(
                top_doctors, many=True, context={"request": request}
            ).data,
            "low_stock_drugs": DrugSerializer(
                low_stock_drugs, many=True, context={"request": request}
            ).data,
        }
    )


# ── Admin Medical Tips Management ─────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_create_tip(request):
    serializer = MedicalTipSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "message": "Medical tip created successfully.",
                "tip": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_update_tip(request, pk):
    try:
        tip = MedicalTip.objects.get(pk=pk)
    except MedicalTip.DoesNotExist:
        return Response({"error": "Tip not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = MedicalTipSerializer(tip, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "message": "Tip updated successfully.",
                "tip": serializer.data,
            }
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_delete_tip(request, pk):
    try:
        tip = MedicalTip.objects.get(pk=pk)
        tip.delete()
        return Response({"message": "Tip deleted successfully."})
    except MedicalTip.DoesNotExist:
        return Response({"error": "Tip not found."}, status=status.HTTP_404_NOT_FOUND)


# ── Doctor Dashboard Overview ──────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_dashboard(request):
    try:
        doctor = Doctor.objects.get(doctor_profile__user=request.user)
    except Doctor.DoesNotExist:
        return Response(
            {"error": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND
        )

    from django.utils import timezone

    today = timezone.now().date()

    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    today_appointments = Appointment.objects.filter(doctor=doctor, date=today).count()
    pending_appointments = Appointment.objects.filter(
        doctor=doctor, status="pending"
    ).count()
    completed_appointments = Appointment.objects.filter(
        doctor=doctor, status="completed"
    ).count()

    upcoming = Appointment.objects.filter(
        doctor=doctor,
        date__gte=today,
        status__in=["pending", "confirmed", "rescheduled"],
    ).order_by("date", "time")[:5]

    return Response(
        {
            "stats": {
                "total_appointments": total_appointments,
                "today_appointments": today_appointments,
                "pending_appointments": pending_appointments,
                "completed_appointments": completed_appointments,
            },
            "upcoming_appointments": AppointmentSerializer(upcoming, many=True).data,
            "doctor": DoctorSerializer(doctor, context={"request": request}).data,
        }
    )


# ── Doctor Appointments ────────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_appointments(request):
    try:
        doctor = Doctor.objects.get(doctor_profile__user=request.user)
    except Doctor.DoesNotExist:
        return Response(
            {"error": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND
        )

    appointments = Appointment.objects.filter(doctor=doctor).order_by("-date", "-time")

    status_filter = request.query_params.get("status")
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    date_filter = request.query_params.get("date")
    if date_filter:
        appointments = appointments.filter(date=date_filter)

    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


# ── Doctor Update Appointment Status ──────────────────────────
@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_update_appointment(request, pk):
    try:
        doctor = Doctor.objects.get(doctor_profile__user=request.user)
        appointment = Appointment.objects.get(pk=pk, doctor=doctor)
    except (Doctor.DoesNotExist, Appointment.DoesNotExist):
        return Response(
            {"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND
        )

    new_status = request.data.get("status")
    valid_statuses = ["confirmed", "completed", "cancelled"]

    if new_status not in valid_statuses:
        return Response(
            {"error": f"Invalid status. Choose from {valid_statuses}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    appointment.status = new_status
    appointment.save()

    return Response(
        {
            "message": f"Appointment status updated to {new_status}.",
            "appointment": AppointmentSerializer(appointment).data,
        }
    )


# ── Doctor Add Clinical Note ───────────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsDoctor])
def add_clinical_note(request, appointment_id):
    try:
        doctor = Doctor.objects.get(doctor_profile__user=request.user)
        appointment = Appointment.objects.get(pk=appointment_id, doctor=doctor)
    except (Doctor.DoesNotExist, Appointment.DoesNotExist):
        return Response(
            {"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND
        )

    note, created = ClinicalNote.objects.get_or_create(
        appointment=appointment,
        doctor=doctor,
        patient=appointment.user,
    )

    note.diagnosis = request.data.get("diagnosis", note.diagnosis)
    note.prescription = request.data.get("prescription", note.prescription)
    note.notes = request.data.get("notes", note.notes)
    note.follow_up_date = request.data.get("follow_up_date", note.follow_up_date)
    note.save()

    serializer = ClinicalNoteSerializer(note)
    return Response(
        {
            "message": "Clinical note saved successfully.",
            "note": serializer.data,
        }
    )


# ── Doctor Get Clinical Notes ──────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsDoctor])
def get_clinical_notes(request):
    try:
        doctor = Doctor.objects.get(doctor_profile__user=request.user)
    except Doctor.DoesNotExist:
        return Response(
            {"error": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND
        )

    notes = ClinicalNote.objects.filter(doctor=doctor).order_by("-created_at")
    serializer = ClinicalNoteSerializer(notes, many=True)
    return Response(serializer.data)


# ── Doctor Update Availability ─────────────────────────────────
@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_update_availability(request):
    try:
        doctor = Doctor.objects.get(doctor_profile__user=request.user)
    except Doctor.DoesNotExist:
        return Response(
            {"error": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND
        )

    availability = request.data.get("availability")
    if availability not in ["available", "busy", "unavailable"]:
        return Response(
            {"error": "Invalid availability status."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    doctor.availability = availability
    doctor.save()

    return Response(
        {
            "message": f"Availability updated to {availability}.",
            "doctor": DoctorSerializer(doctor, context={"request": request}).data,
        }
    )


# ── Doctor Manage Time Slots ───────────────────────────────────
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_time_slots(request):
    try:
        doctor = Doctor.objects.get(doctor_profile__user=request.user)
    except Doctor.DoesNotExist:
        return Response(
            {"error": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        slots = DoctorTimeSlot.objects.filter(doctor=doctor)
        serializer = DoctorTimeSlotSerializer(slots, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        serializer = DoctorTimeSlotSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(doctor=doctor)
            return Response(
                {
                    "message": "Time slot added successfully.",
                    "slot": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Doctor Update Profile ──────────────────────────────────────
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_profile(request):
    try:
        doctor = Doctor.objects.get(doctor_profile__user=request.user)
        profile = DoctorProfile.objects.get(user=request.user)
    except (Doctor.DoesNotExist, DoctorProfile.DoesNotExist):
        return Response(
            {"error": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        return Response(
            {
                "doctor": DoctorSerializer(doctor, context={"request": request}).data,
                "profile": DoctorProfileSerializer(profile).data,
            }
        )

    if request.method == "PUT":
        doctor.name = request.data.get("name", doctor.name)
        doctor.bio = request.data.get("bio", doctor.bio)
        doctor.consultation_fee = request.data.get(
            "consultation_fee", doctor.consultation_fee
        )
        doctor.save()

        profile_serializer = DoctorProfileSerializer(
            profile, data=request.data, partial=True
        )
        if profile_serializer.is_valid():
            profile_serializer.save()

        return Response(
            {
                "message": "Profile updated successfully.",
                "doctor": DoctorSerializer(doctor, context={"request": request}).data,
                "profile": DoctorProfileSerializer(profile).data,
            }
        )


# ── Pharmacist Dashboard ───────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsPharmacist])
def pharmacist_dashboard(request):
    total_drugs = Drug.objects.count()
    low_stock = Drug.objects.filter(stock__lte=10).count()
    out_of_stock = Drug.objects.filter(stock=0).count()
    pending_orders = DrugOrder.objects.filter(status="pending").count()
    processing_orders = DrugOrder.objects.filter(status="processing").count()
    dispensed_orders = DrugOrder.objects.filter(status="dispensed").count()

    recent_orders = DrugOrder.objects.order_by("-created_at")[:5]
    low_stock_drugs = Drug.objects.filter(stock__lte=10).order_by("stock")[:5]

    return Response(
        {
            "stats": {
                "total_drugs": total_drugs,
                "low_stock": low_stock,
                "out_of_stock": out_of_stock,
                "pending_orders": pending_orders,
                "processing_orders": processing_orders,
                "dispensed_orders": dispensed_orders,
            },
            "recent_orders": DrugOrderSerializer(recent_orders, many=True).data,
            "low_stock_drugs": DrugSerializer(
                low_stock_drugs, many=True, context={"request": request}
            ).data,
        }
    )


# ── Pharmacist Drug Inventory ──────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsPharmacistOrAdmin])
def pharmacist_drug_list(request):
    drugs = Drug.objects.all().order_by("name")

    search = request.query_params.get("search")
    if search:
        drugs = drugs.filter(name__icontains=search)

    category = request.query_params.get("category")
    if category:
        drugs = drugs.filter(category=category)

    low_stock = request.query_params.get("low_stock")
    if low_stock:
        drugs = drugs.filter(stock__lte=10)

    serializer = DrugSerializer(drugs, many=True, context={"request": request})
    return Response(serializer.data)


# ── Pharmacist Update Drug Stock ───────────────────────────────
@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsPharmacistOrAdmin])
def pharmacist_update_stock(request, pk):
    try:
        drug = Drug.objects.get(pk=pk)
    except Drug.DoesNotExist:
        return Response({"error": "Drug not found."}, status=status.HTTP_404_NOT_FOUND)

    new_stock = request.data.get("stock")
    if new_stock is None:
        return Response(
            {"error": "Stock value is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    drug.stock = int(new_stock)
    drug.save()

    return Response(
        {
            "message": f"Stock updated to {new_stock} for {drug.name}.",
            "drug": DrugSerializer(drug, context={"request": request}).data,
        }
    )


# ── Pharmacist Order List ──────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsPharmacistOrAdmin])
def pharmacist_order_list(request):
    orders = DrugOrder.objects.all().order_by("-created_at")

    status_filter = request.query_params.get("status")
    if status_filter:
        orders = orders.filter(status=status_filter)

    serializer = DrugOrderSerializer(orders, many=True)
    return Response(serializer.data)


# ── Pharmacist Update Order Status ────────────────────────────
@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsPharmacistOrAdmin])
def pharmacist_update_order(request, pk):
    try:
        order = DrugOrder.objects.get(pk=pk)
    except DrugOrder.DoesNotExist:
        return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get("status")
    valid_statuses = ["processing", "dispensed", "cancelled"]

    if new_status not in valid_statuses:
        return Response(
            {"error": f"Invalid status. Choose from {valid_statuses}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    order.status = new_status
    order.pharmacist = request.user
    order.notes = request.data.get("notes", order.notes)
    order.save()

    # Reduce stock when dispensed
    if new_status == "dispensed":
        for item in order.items:
            try:
                drug = Drug.objects.get(pk=item["drug_id"])
                drug.stock = max(0, drug.stock - item["quantity"])
                drug.save()
            except Drug.DoesNotExist:
                pass

    return Response(
        {
            "message": f"Order status updated to {new_status}.",
            "order": DrugOrderSerializer(order).data,
        }
    )


# ── Patient Place Order ────────────────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def place_order(request):
    cart_items = CartItem.objects.filter(user=request.user)

    if not cart_items.exists():
        return Response(
            {"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST
        )

    items = []
    total_amount = 0

    for item in cart_items:
        if item.drug.stock < item.quantity:
            return Response(
                {
                    "error": f"Insufficient stock for {item.drug.name}. Available: {item.drug.stock}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        items.append(
            {
                "drug_id": item.drug.id,
                "drug_name": item.drug.name,
                "quantity": item.quantity,
                "price": str(item.drug.price),
                "total": str(item.total_price),
            }
        )
        total_amount += item.total_price

    order = DrugOrder.objects.create(
        user=request.user,
        items=items,
        total_amount=total_amount,
        prescription_ref=request.data.get("prescription_ref", ""),
    )

    # Clear cart after order
    cart_items.delete()

    return Response(
        {
            "message": "Order placed successfully.",
            "order": DrugOrderSerializer(order).data,
        },
        status=status.HTTP_201_CREATED,
    )


# ── Patient Order History ──────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def patient_order_history(request):
    orders = DrugOrder.objects.filter(user=request.user).order_by("-created_at")
    serializer = DrugOrderSerializer(orders, many=True)
    return Response(serializer.data)


# ── Register ───────────────────────────────────────────────────
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        session_id = user.profile.generate_session_id()
        tokens = get_tokens_for_user(user, session_id)
        return Response(
            {
                "message": "Account created successfully.",
                "user": UserSerializer(user).data,
                "tokens": tokens,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Login ──────────────────────────────────────────────────────
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"error": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED
        )

    profile = user.profile

    # Check if account is locked
    if profile.is_locked():
        return Response(
            {
                "error": f"Account locked due to too many failed attempts. Try again after {profile.locked_until.strftime('%H:%M:%S')}."
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # Authenticate
    auth_user = authenticate(request, username=email, password=password)

    if not auth_user:
        profile.login_attempts += 1
        if profile.login_attempts >= 5:
            profile.locked_until = timezone.now() + timedelta(minutes=30)
            profile.login_attempts = 0
        profile.save()
        return Response(
            {"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED
        )

    # Reset failed attempts
    profile.login_attempts = 0
    profile.locked_until = None
    profile.last_login_ip = get_client_ip(request)
    profile.last_login_device = request.META.get("HTTP_USER_AGENT", "")[:200]

    # Generate new session ID — invalidates all previous sessions
    session_id = profile.generate_session_id()
    profile.save()

    tokens = get_tokens_for_user(auth_user, session_id)

    return Response(
        {
            "message": "Login successful.",
            "user": UserSerializer(auth_user).data,
            "tokens": tokens,
        },
        status=status.HTTP_200_OK,
    )


# ── Logout ─────────────────────────────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()

        # Clear session ID
        request.user.profile.session_id = None
        request.user.profile.save()

        return Response({"message": "Logged out successfully."})
    except Exception:
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


# ── Get Profile ────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# ── Update Profile ─────────────────────────────────────────────
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    user.first_name = request.data.get("first_name", user.first_name)
    user.last_name = request.data.get("last_name", user.last_name)
    user.save()

    profile_serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    if profile_serializer.is_valid():
        profile_serializer.save()

    return Response(
        {
            "message": "Profile updated successfully.",
            "user": UserSerializer(user).data,
        }
    )


# ── Change Password ────────────────────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    user = request.user
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    if not user.check_password(old_password):
        return Response(
            {"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST
        )

    if len(new_password) < 6:
        return Response(
            {"error": "New password must be at least 6 characters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.set_password(new_password)
    user.save()

    # Force re-login by clearing session
    user.profile.session_id = None
    user.profile.save()

    return Response({"message": "Password changed successfully. Please log in again."})


# ── List Doctors ───────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([AllowAny])
def doctor_list(request):
    doctors = Doctor.objects.all()

    search = request.query_params.get("search")
    if search:
        doctors = doctors.filter(name__icontains=search)

    specialty = request.query_params.get("specialty")
    if specialty and specialty != "All":
        doctors = doctors.filter(specialty__icontains=specialty)

    availability = request.query_params.get("availability")
    if availability:
        doctors = doctors.filter(availability=availability)

    serializer = DoctorSerializer(doctors, many=True, context={"request": request})
    return Response(serializer.data)


# ── Doctor Detail ──────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([AllowAny])
def doctor_detail(request, pk):
    try:
        doctor = Doctor.objects.get(pk=pk)
    except Doctor.DoesNotExist:
        return Response(
            {"error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = DoctorSerializer(doctor, context={"request": request})
    return Response(serializer.data)


# ── Doctor Specialties ─────────────────────────────────────────
@api_view(["GET"])
@permission_classes([AllowAny])
def doctor_specialties(request):
    specialties = Doctor.objects.values_list("specialty", flat=True).distinct()
    return Response(list(specialties))


# ── List Drugs ─────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([AllowAny])
def drug_list(request):
    drugs = Drug.objects.all()

    search = request.query_params.get("search")
    if search:
        drugs = drugs.filter(name__icontains=search)

    category = request.query_params.get("category")
    if category and category != "All":
        drugs = drugs.filter(category__icontains=category)

    serializer = DrugSerializer(drugs, many=True, context={"request": request})
    return Response(serializer.data)


# ── Drug Detail ────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([AllowAny])
def drug_detail(request, pk):
    try:
        drug = Drug.objects.get(pk=pk)
    except Drug.DoesNotExist:
        return Response({"error": "Drug not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = DrugSerializer(drug, context={"request": request})
    return Response(serializer.data)


# ── Drug Categories ────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([AllowAny])
def drug_categories(request):
    categories = Drug.objects.values_list("category", flat=True).distinct()
    return Response(list(categories))


# ── Get Cart ───────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    serializer = CartItemSerializer(cart_items, many=True, context={"request": request})
    return Response(serializer.data)


# ── Add to Cart ────────────────────────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    drug_id = request.data.get("drug_id")
    quantity = request.data.get("quantity", 1)

    try:
        drug = Drug.objects.get(pk=drug_id)
    except Drug.DoesNotExist:
        return Response({"error": "Drug not found."}, status=status.HTTP_404_NOT_FOUND)

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user, drug=drug, defaults={"quantity": quantity}
    )

    if not created:
        cart_item.quantity += int(quantity)
        cart_item.save()

    serializer = CartItemSerializer(cart_item, context={"request": request})
    return Response(
        {"message": "Added to cart successfully.", "cart_item": serializer.data},
        status=status.HTTP_201_CREATED,
    )


# ── Update Cart Item ───────────────────────────────────────────
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_cart_item(request, pk):
    try:
        cart_item = CartItem.objects.get(pk=pk, user=request.user)
    except CartItem.DoesNotExist:
        return Response(
            {"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND
        )

    quantity = request.data.get("quantity")
    if quantity and int(quantity) > 0:
        cart_item.quantity = int(quantity)
        cart_item.save()
    elif quantity and int(quantity) <= 0:
        cart_item.delete()
        return Response({"message": "Item removed from cart."})

    serializer = CartItemSerializer(cart_item, context={"request": request})
    return Response(serializer.data)


# ── Remove from Cart ───────────────────────────────────────────
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, pk):
    try:
        cart_item = CartItem.objects.get(pk=pk, user=request.user)
        cart_item.delete()
        return Response({"message": "Item removed from cart."})
    except CartItem.DoesNotExist:
        return Response(
            {"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND
        )


# ── Clear Cart ─────────────────────────────────────────────────
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    CartItem.objects.filter(user=request.user).delete()
    return Response({"message": "Cart cleared successfully."})


# ── Book Appointment ───────────────────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def book_appointment(request):
    doctor_id = request.data.get("doctor_id")
    date = request.data.get("date")
    time = request.data.get("time")
    description = request.data.get("description", "")

    if not doctor_id or not date or not time:
        return Response(
            {"error": "Doctor, date and time are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        doctor = Doctor.objects.get(pk=doctor_id)
    except Doctor.DoesNotExist:
        return Response(
            {"error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = AppointmentSerializer(
        data={
            "doctor_id": doctor_id,
            "date": date,
            "time": time,
            "description": description,
        }
    )

    if serializer.is_valid():
        appointment = serializer.save(user=request.user, doctor=doctor)
        return Response(
            {
                "message": f"Appointment booked successfully with Dr. {doctor.name}.",
                "appointment": AppointmentSerializer(appointment).data,
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── List User Appointments ─────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def appointment_list(request):
    appointments = Appointment.objects.filter(user=request.user).order_by("-created_at")

    status_filter = request.query_params.get("status")
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


# ── Appointment Detail ─────────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def appointment_detail(request, pk):
    try:
        appointment = Appointment.objects.get(pk=pk, user=request.user)
    except Appointment.DoesNotExist:
        return Response(
            {"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data)


# ── Reschedule Appointment ─────────────────────────────────────
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def reschedule_appointment(request, pk):
    try:
        appointment = Appointment.objects.get(pk=pk, user=request.user)
    except Appointment.DoesNotExist:
        return Response(
            {"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND
        )

    if appointment.status in ["completed", "cancelled"]:
        return Response(
            {"error": "Cannot reschedule a completed or cancelled appointment."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    new_date = request.data.get("date")
    new_time = request.data.get("time")

    if not new_date or not new_time:
        return Response(
            {"error": "New date and time are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    appointment.date = new_date
    appointment.time = new_time
    appointment.status = "rescheduled"
    appointment.save()

    serializer = AppointmentSerializer(appointment)
    return Response(
        {
            "message": "Appointment rescheduled successfully.",
            "appointment": serializer.data,
        }
    )


# ── Cancel Appointment ─────────────────────────────────────────
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def cancel_appointment(request, pk):
    try:
        appointment = Appointment.objects.get(pk=pk, user=request.user)
    except Appointment.DoesNotExist:
        return Response(
            {"error": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND
        )

    if appointment.status in ["completed", "cancelled"]:
        return Response(
            {"error": "Appointment is already completed or cancelled."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    appointment.status = "cancelled"
    appointment.save()

    return Response({"message": "Appointment cancelled successfully."})


# ── List Medical Tips ──────────────────────────────────────────
@api_view(["GET"])
@permission_classes([AllowAny])
def medical_tip_list(request):
    tips = MedicalTip.objects.filter(is_active=True)

    category = request.query_params.get("category")
    if category:
        tips = tips.filter(category=category)

    serializer = MedicalTipSerializer(tips, many=True)
    return Response(serializer.data)


# ── Daily Tip ──────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([AllowAny])
def daily_tip(request):
    tips = MedicalTip.objects.filter(is_active=True)
    if not tips.exists():
        return Response(
            {"error": "No tips available."}, status=status.HTTP_404_NOT_FOUND
        )

    tip = random.choice(list(tips))
    serializer = MedicalTipSerializer(tip)
    return Response(serializer.data)


# ── Tip Detail ─────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([AllowAny])
def medical_tip_detail(request, pk):
    try:
        tip = MedicalTip.objects.get(pk=pk, is_active=True)
    except MedicalTip.DoesNotExist:
        return Response({"error": "Tip not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = MedicalTipSerializer(tip)
    return Response(serializer.data)


# ── Chatbot Proxy ──────────────────────────────────────────────
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chatbot(request):
    messages = request.data.get("messages", [])

    if not messages:
        return Response(
            {"error": "Messages are required."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        from django.conf import settings
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-pro")

        system_prompt = (
            "You are PrimeHealth Assistant, a helpful and friendly virtual health assistant "
            "for PrimeHealth, a Nigerian healthcare platform. "
            "You can help users with general health questions, appointment tracking, "
            "platform features, wellness tips and pharmacy questions. "
            "Never diagnose conditions or prescribe medications. "
            "Always recommend consulting a real doctor for serious concerns. "
            "Keep responses short and easy to read."
        )

        conversation = "\n".join(
            [
                f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
                for m in messages
            ]
        )

        full_prompt = f"{system_prompt}\n\nConversation:\n{conversation}\n\nAssistant:"

        response = model.generate_content(full_prompt)

        return Response({"reply": response.text})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
