from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.groups.models import GroupInvite, GroupMembership


class GroupInviteCommand:
    def __init__(self, invite, actor):
        self.invite = invite
        self.actor = actor

    def execute(self):
        raise NotImplementedError

    def _ensure_pending_invite(self):
        if self.invite.status != GroupInvite.InviteStatus.PENDING:
            raise ValidationError("Apenas convites pendentes podem ser respondidos.")

    def _respond(self, status):
        self.invite.status = status
        self.invite.responded_at = timezone.now()
        self.invite.save(update_fields=["status", "responded_at"])
        return self.invite


class RecipientGroupInviteCommand(GroupInviteCommand):
    def _validate_actor(self):
        if self.invite.sent_to_id != self.actor.id:
            raise PermissionDenied("Apenas o destinatario pode responder ao convite.")


class AcceptGroupInviteCommand(RecipientGroupInviteCommand):
    def execute(self):
        self._validate_actor()
        self._ensure_pending_invite()
        self._activate_membership()
        return self._respond(GroupInvite.InviteStatus.ACCEPTED)

    def _activate_membership(self):
        membership = GroupMembership.objects.filter(
            user=self.invite.sent_to,
            group=self.invite.group,
        ).first()

        if membership is None:
            GroupMembership.objects.create(
                user=self.invite.sent_to,
                group=self.invite.group,
                role=GroupMembership.MembershipRole.MEMBER,
                is_active=True,
            )
            return

        membership.role = GroupMembership.MembershipRole.MEMBER
        membership.is_active = True
        membership.save(update_fields=["role", "is_active"])


class DeclineGroupInviteCommand(RecipientGroupInviteCommand):
    def execute(self):
        self._validate_actor()
        self._ensure_pending_invite()
        return self._respond(GroupInvite.InviteStatus.DECLINED)


class CancelGroupInviteCommand(GroupInviteCommand):
    def execute(self):
        self._validate_actor()
        self._ensure_pending_invite()
        return self._respond(GroupInvite.InviteStatus.CANCELED)

    def _validate_actor(self):
        if self.invite.sent_by_id != self.actor.id:
            raise PermissionDenied("Apenas quem enviou o convite pode cancelá-lo.")
