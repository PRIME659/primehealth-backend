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
    # Chatbot
    path("chatbot/", views.chatbot, name="HealthBot"),
    # Doctor Portal
    path("doctor/dashboard/", views.doctor_dashboard, name="doctor_dashboard"),
    path("doctor/appointments/", views.doctor_appointments, name="doctor_appointments"),
    path(
        "doctor/appointments/<int:pk>/update/",
        views.doctor_update_appointment,
        name="doctor_update_appointment",
    ),
    path(
        "doctor/appointments/<int:appointment_id>/notes/",
        views.add_clinical_note,
        name="add_clinical_note",
    ),
    path("doctor/notes/", views.get_clinical_notes, name="get_clinical_notes"),
    path(
        "doctor/availability/",
        views.doctor_update_availability,
        name="doctor_update_availability",
    ),
    path("doctor/time-slots/", views.doctor_time_slots, name="doctor_time_slots"),
    path("doctor/profile/", views.doctor_profile, name="doctor_profile"),
    # Admin Portal
    path("admin-portal/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-portal/users/", views.admin_user_list, name="admin_user_list"),
    path(
        "admin-portal/users/<int:pk>/",
        views.admin_user_detail,
        name="admin_user_detail",
    ),
    path(
        "admin-portal/users/<int:pk>/toggle/",
        views.admin_toggle_user,
        name="admin_toggle_user",
    ),
    path(
        "admin-portal/doctors/create/",
        views.admin_create_doctor,
        name="admin_create_doctor",
    ),
    path(
        "admin-portal/doctors/<int:pk>/update/",
        views.admin_update_doctor,
        name="admin_update_doctor",
    ),
    path(
        "admin-portal/doctors/<int:pk>/delete/",
        views.admin_delete_doctor,
        name="admin_delete_doctor",
    ),
    path(
        "admin-portal/appointments/",
        views.admin_appointment_list,
        name="admin_appointment_list",
    ),
    path(
        "admin-portal/appointments/<int:pk>/update/",
        views.admin_update_appointment,
        name="admin_update_appointment",
    ),
    path(
        "admin-portal/drugs/create/", views.admin_create_drug, name="admin_create_drug"
    ),
    path(
        "admin-portal/drugs/<int:pk>/update/",
        views.admin_update_drug,
        name="admin_update_drug",
    ),
    path(
        "admin-portal/drugs/<int:pk>/delete/",
        views.admin_delete_drug,
        name="admin_delete_drug",
    ),
    path("admin-portal/analytics/", views.admin_analytics, name="admin_analytics"),
    path("admin-portal/tips/create/", views.admin_create_tip, name="admin_create_tip"),
    path(
        "admin-portal/tips/<int:pk>/update/",
        views.admin_update_tip,
        name="admin_update_tip",
    ),
    path(
        "admin-portal/tips/<int:pk>/delete/",
        views.admin_delete_tip,
        name="admin_delete_tip",
    ),
    # Pharmacist Portal
    path(
        "pharmacist/dashboard/", views.pharmacist_dashboard, name="pharmacist_dashboard"
    ),
    path("pharmacist/drugs/", views.pharmacist_drug_list, name="pharmacist_drug_list"),
    path(
        "pharmacist/drugs/<int:pk>/stock/",
        views.pharmacist_update_stock,
        name="pharmacist_update_stock",
    ),
    path(
        "pharmacist/orders/", views.pharmacist_order_list, name="pharmacist_order_list"
    ),
    path(
        "pharmacist/orders/<int:pk>/update/",
        views.pharmacist_update_order,
        name="pharmacist_update_order",
    ),
    # Patient Orders
    path("orders/place/", views.place_order, name="place_order"),
    path("orders/history/", views.patient_order_history, name="patient_order_history"),
]
