from rest_framework.permissions import BasePermission, SAFE_METHODS
class EstAdministrateur(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "ADMINISTRATEUR")
class EstReparateur(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "REPARATEUR")


class EstAdministrateurOuLectureSeule(BasePermission):
    """Les données publiques restent lisibles, leur gestion est réservée à l'admin."""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or EstAdministrateur().has_permission(request, view)
