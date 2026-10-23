from rest_framework import permissions


class EsAdminOSoloLectura(permissions.BasePermission):
    """Permite lectura publica y restringe escritura a administradores."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class EsDuenioOAdmin(permissions.BasePermission):
    """Permite acceso a administradores o al cliente propietario del recurso."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True

        # Para objetos Cliente directos
        if hasattr(obj, "usuario"):
            return obj.usuario == request.user

        # Para objetos con relacion a cliente (Receta, Turno, Pedido, Resena)
        if hasattr(obj, "cliente"):
            return hasattr(request.user, "cliente") and obj.cliente == request.user.cliente

        return False


class EsDuenioResenaOAdmin(permissions.BasePermission):
    """Lectura publica; creacion y modificacion solo para el autor o staff."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        return hasattr(request.user, "cliente") and obj.cliente == request.user.cliente
