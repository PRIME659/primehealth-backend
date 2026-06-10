from rest_framework.permissions import BasePermission
from django.utils import timezone


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role == "patient"
        )


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role == "doctor"
        )


class IsPharmacist(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role == "pharmacist"
        )


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role in ["admin", "super_admin"]
        )


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role == "super_admin"
        )


class IsDoctorOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role in ["doctor", "admin", "super_admin"]
        )


class IsPharmacistOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role in ["pharmacist", "admin", "super_admin"]
        )


class SessionValid(BasePermission):
    message = "Your session has been terminated. Please log in again."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if not hasattr(request.user, "profile"):
            return False

        profile = request.user.profile
        token_session_id = request.auth.get("session_id") if request.auth else None

        if not token_session_id:
            return False

        return profile.session_id == token_session_id
