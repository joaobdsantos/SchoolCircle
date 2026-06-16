from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.groups.models import GroupInvite, GroupMembership, StudyGroup
from apps.groups.permissions import IsActiveGroupMember
from apps.groups.serializers import (
    GroupInviteSerializer,
    GroupMembershipSerializer,
    GroupRankingSerializer,
    StudyGroupSerializer,
)


def _get_active_membership(user, group):
    return (
        GroupMembership.objects.filter(
            user=user,
            group=group,
            is_active=True,
        )
        .select_related("user", "group")
        .first()
    )


def _ensure_pending_invite(invite):
    if invite.status != GroupInvite.InviteStatus.PENDING:
        raise ValidationError("Apenas convites pendentes podem ser respondidos.")


class StudyGroupListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = StudyGroup.objects.all().order_by("name")
    serializer_class = StudyGroupSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            group = serializer.save()
            GroupMembership.objects.create(
                user=self.request.user,
                group=group,
                role=GroupMembership.MembershipRole.OWNER,
            )


class StudyGroupDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = StudyGroup.objects.all()
    serializer_class = StudyGroupSerializer
    lookup_field = "id"
    lookup_url_kwarg = "group_id"


class GroupInviteListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GroupInviteSerializer

    def get_queryset(self):
        return (
            GroupInvite.objects.filter(
                sent_to=self.request.user,
                status=GroupInvite.InviteStatus.PENDING,
            )
            .select_related("group", "sent_by", "sent_to")
            .order_by("-sent_at")
        )

    def perform_create(self, serializer):
        group_id = self.request.data.get("group")
        if not group_id:
            raise ValidationError({"group": "Grupo e obrigatorio."})

        group = get_object_or_404(StudyGroup, id=group_id)
        owner_membership = _get_active_membership(self.request.user, group)
        if (
            owner_membership is None
            or owner_membership.role != GroupMembership.MembershipRole.OWNER
        ):
            raise PermissionDenied("Apenas o owner do grupo pode criar convites.")

        with transaction.atomic():
            serializer.save(sent_by=self.request.user)


class GroupInviteDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GroupInviteSerializer
    lookup_field = "id"
    lookup_url_kwarg = "invite_id"

    def get_queryset(self):
        return GroupInvite.objects.filter(
            sent_by=self.request.user,
        ).select_related("group", "sent_by", "sent_to") | GroupInvite.objects.filter(
            sent_to=self.request.user,
        ).select_related("group", "sent_by", "sent_to")


class GroupInviteActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    invite_status = None
    requires_sender = False

    def post(self, request, invite_id):
        with transaction.atomic():
            invite = get_object_or_404(
                GroupInvite.objects.select_for_update().select_related(
                    "group",
                    "sent_by",
                    "sent_to",
                ),
                id=invite_id,
            )

            self._validate_actor(request, invite)
            _ensure_pending_invite(invite)

            if self.invite_status == GroupInvite.InviteStatus.ACCEPTED:
                self._accept_invite(invite)
            else:
                invite.status = self.invite_status
                invite.responded_at = timezone.now()
                invite.save(update_fields=["status", "responded_at"])

            return Response(
                GroupInviteSerializer(invite).data, status=status.HTTP_200_OK
            )

    def _validate_actor(self, request, invite):
        if self.requires_sender:
            if invite.sent_by_id != request.user.id:
                raise PermissionDenied("Apenas quem enviou o convite pode cancelá-lo.")
            return

        if invite.sent_to_id != request.user.id:
            raise PermissionDenied("Apenas o destinatario pode responder ao convite.")

    def _accept_invite(self, invite):
        membership = GroupMembership.objects.filter(
            user=invite.sent_to,
            group=invite.group,
        ).first()

        if membership is None:
            GroupMembership.objects.create(
                user=invite.sent_to,
                group=invite.group,
                role=GroupMembership.MembershipRole.MEMBER,
                is_active=True,
            )
        else:
            membership.role = GroupMembership.MembershipRole.MEMBER
            membership.is_active = True
            membership.save(update_fields=["role", "is_active"])

        invite.status = self.invite_status
        invite.responded_at = timezone.now()
        invite.save(update_fields=["status", "responded_at"])


class GroupInviteAcceptView(GroupInviteActionView):
    invite_status = GroupInvite.InviteStatus.ACCEPTED


class GroupInviteDeclineView(GroupInviteActionView):
    invite_status = GroupInvite.InviteStatus.DECLINED


class GroupInviteCancelView(GroupInviteActionView):
    invite_status = GroupInvite.InviteStatus.CANCELED
    requires_sender = True


class GroupMembershipListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsActiveGroupMember]
    serializer_class = GroupMembershipSerializer

    def get_queryset(self):
        return (
            GroupMembership.objects.filter(
                group_id=self.kwargs["group_id"],
                is_active=True,
            )
            .select_related("user", "group", "user__progress")
            .order_by(
                "-group_points",
                "joined_at",
            )
        )


class GroupMembershipDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, IsActiveGroupMember]
    serializer_class = GroupMembershipSerializer
    lookup_field = "id"
    lookup_url_kwarg = "membership_id"

    def get_queryset(self):
        return GroupMembership.objects.filter(
            group_id=self.kwargs["group_id"],
            is_active=True,
        ).select_related("user", "group", "user__progress")


class GroupMembershipLeaveView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsActiveGroupMember]

    def delete(self, request, group_id, membership_id):
        with transaction.atomic():
            membership = get_object_or_404(
                GroupMembership.objects.select_for_update().select_related(
                    "group",
                    "user",
                ),
                id=membership_id,
                group_id=group_id,
                is_active=True,
            )

            if membership.user_id != request.user.id:
                raise PermissionDenied("Apenas o proprio membro pode sair do grupo.")

            active_members = GroupMembership.objects.filter(
                group_id=group_id,
                is_active=True,
            )

            if active_members.count() <= 1:
                raise ValidationError("Grupo precisa ter pelo menos um membro ativo.")

            if membership.role == GroupMembership.MembershipRole.OWNER:
                raise ValidationError(
                    "Owner nao pode sair sem transferir a responsabilidade."
                )

            membership.is_active = False
            membership.save(update_fields=["is_active"])

        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupRankingView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = GroupRankingSerializer

    def get_queryset(self):
        group = get_object_or_404(StudyGroup, id=self.kwargs["group_id"])
        memberships = list(
            GroupMembership.objects.filter(
                group=group,
                is_active=True,
            )
            .select_related("user", "user__progress", "group")
            .order_by(
                "-group_points",
                "joined_at",
            )
        )

        last_points = None
        calculated_rank = 0
        for index, membership in enumerate(memberships, start=1):
            if last_points is None or membership.group_points != last_points:
                calculated_rank = index
                last_points = membership.group_points
            membership.calculated_rank = calculated_rank

        return memberships
