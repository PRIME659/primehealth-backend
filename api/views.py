from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UserSerializer, UserProfileSerializer, DoctorSerializer, DrugSerializer, CartItemSerializer, AppointmentSerializer, MedicalTipSerializer
from .models import UserProfile
from .models import Doctor, Drug, CartItem, Appointment, MedicalTip
import anthropic
import random


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response(
            {
                "message": "Account created successfully.",
                "user": UserSerializer(user).data,
                "tokens": tokens,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

    user = authenticate(request, username=email, password=password)
    if not user:
        return Response(
            {"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED
        )

    tokens = get_tokens_for_user(user)
    return Response(
        {
            "message": "Login successful.",
            "user": UserSerializer(user).data,
            "tokens": tokens,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(
            {"message": "Logged out successfully."}, status=status.HTTP_200_OK
        )
    except Exception:
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


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
    return Response({"message": "Password changed successfully."})


# ── List Doctors ───────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([AllowAny])
def doctor_list(request):
    doctors = Doctor.objects.all()

    # Search by name
    search = request.query_params.get("search")
    if search:
        doctors = doctors.filter(name__icontains=search)

    # Filter by specialty
    specialty = request.query_params.get("specialty")
    if specialty and specialty != "All":
        doctors = doctors.filter(specialty__icontains=specialty)

    # Filter by availability
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

    tip = random.choice(tips)
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

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system="""You are PrimeHealth Assistant, a helpful and friendly virtual health assistant for PrimeHealth — a Nigerian healthcare platform.

You can help users with:
- General health questions and medical information
- Tracking and understanding their appointments
- Explaining how to use PrimeHealth features
- General wellness tips and advice
- Answering questions about medications and pharmacy

Important rules:
- Always be warm, professional and concise
- Never diagnose conditions or prescribe medications
- Always recommend consulting a real doctor for serious medical concerns
- Keep responses short and easy to read
- You are not a replacement for professional medical advice""",
            messages=messages,
        )

        return Response({"reply": response.content[0].text})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
