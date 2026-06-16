from rest_framework.permissions import BasePermission

from apps.groups.models import GroupMembership


class IsActiveGroupMember(BasePermission):
    message = "Usuario precisa ser membro ativo do grupo."

    def has_permission(self, request, view):
        group_id = (
            request.data.get("shared_group")
            or request.data.get("group")
            or view.kwargs.get("group_id")
        )

        if not group_id:
            return True

        return GroupMembership.objects.filter(
            user=request.user,
            group_id=group_id,
            is_active=True,
        ).exists()
