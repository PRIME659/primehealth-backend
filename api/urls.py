from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path("auth/register/", views.register, name="register"),
    path("auth/login/", views.login, name="login"),
    path("auth/logout/", views.logout, name="logout"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Profile
    path("auth/profile/", views.get_profile, name="get_profile"),
    path("auth/profile/update/", views.update_profile, name="update_profile"),
    path("auth/password/change/", views.change_password, name="change_password"),
    # Doctors
    path("doctors/", views.doctor_list, name="doctor_list"),
    path("doctors/<int:pk>/", views.doctor_detail, name="doctor_detail"),
    path("doctors/specialties/", views.doctor_specialties, name="doctor_specialties"),
    # Pharmacy
    path("pharmacy/", views.drug_list, name="drug_list"),
    path("pharmacy/<int:pk>/", views.drug_detail, name="drug_detail"),
    path("pharmacy/categories/", views.drug_categories, name="drug_categories"),
    # Cart
    path("cart/", views.get_cart, name="get_cart"),
    path("cart/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/<int:pk>/update/", views.update_cart_item, name="update_cart_item"),
    path("cart/<int:pk>/remove/", views.remove_from_cart, name="remove_from_cart"),
    path("cart/clear/", views.clear_cart, name="clear_cart"),
    # Appointments
    path("appointments/", views.appointment_list, name="appointment_list"),
    path("appointments/book/", views.book_appointment, name="book_appointment"),
    path("appointments/<int:pk>/", views.appointment_detail, name="appointment_detail"),
    path(
        "appointments/<int:pk>/reschedule/",
        views.reschedule_appointment,
        name="reschedule_appointment",
    ),
    path(
        "appointments/<int:pk>/cancel/",
        views.cancel_appointment,
        name="cancel_appointment",
    ),
    # Medical Tips
    path("tips/", views.medical_tip_list, name="medical_tip_list"),
    path("tips/daily/", views.daily_tip, name="daily_tip"),
    path("tips/<int:pk>/", views.medical_tip_detail, name="medical_tip_detail"),
    # ChatBot
    path("chatbot/", views.chatbot, name="chatbot"),
]
