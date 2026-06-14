import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class StudyGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_group(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self.save(update_fields=["name", "description", "updated_at"])

    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    class MembershipRole(models.TextChoices):
        OWNER = "OWNER", "Owner"
        MEMBER = "MEMBER", "Member"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="group_memberships",
    )
    group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=MembershipRole.choices,
        default=MembershipRole.MEMBER,
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    group_points = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "group"],
                name="unique_group_membership_user_group",
            ),
            models.CheckConstraint(
                condition=models.Q(group_points__gte=0),
                name="group_membership_group_points_gte_0",
            ),
        ]

    @property
    def rank(self):
        if not self.is_active:
            return None

        higher_score_count = GroupMembership.objects.filter(
            group=self.group,
            is_active=True,
            group_points__gt=self.group_points,
        ).count()
        return higher_score_count + 1

    def __str__(self):
        return f"GroupMembership(user_id={self.user_id}, group_id={self.group_id})"


class GroupInvite(models.Model):
    class InviteStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        DECLINED = "DECLINED", "Declined"
        CANCELED = "CANCELED", "Canceled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(
        StudyGroup,
        on_delete=models.CASCADE,
        related_name="invites",
    )
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_group_invites",
    )
    sent_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_group_invites",
    )
    status = models.CharField(
        max_length=20,
        choices=InviteStatus.choices,
        default=InviteStatus.PENDING,
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(sent_by=models.F("sent_to")),
                name="group_invite_sent_by_not_sent_to",
            ),
            models.UniqueConstraint(
                fields=["group", "sent_to"],
                condition=models.Q(status="PENDING"),
                name="unique_pending_group_invite_group_sent_to",
            ),
        ]

    def clean(self):
        errors = {}

        if self.sent_by_id and self.sent_to_id and self.sent_by_id == self.sent_to_id:
            errors["sent_to"] = "Usuario nao pode convidar a si mesmo."

        if self.status == self.InviteStatus.PENDING and self.responded_at is not None:
            errors["responded_at"] = "Convite pendente nao deve ter data de resposta."

        if self.status != self.InviteStatus.PENDING and self.responded_at is None:
            errors["responded_at"] = "Convite respondido deve ter data de resposta."

        if self.group_id and self.sent_to_id:
            active_membership_exists = GroupMembership.objects.filter(
                group_id=self.group_id,
                user_id=self.sent_to_id,
                is_active=True,
            ).exists()
            if active_membership_exists:
                errors["sent_to"] = "Usuario ja e membro ativo deste grupo."

        if (
            self.status == self.InviteStatus.PENDING
            and self.group_id
            and self.sent_to_id
        ):
            pending_invite_exists = GroupInvite.objects.filter(
                group_id=self.group_id,
                sent_to_id=self.sent_to_id,
                status=self.InviteStatus.PENDING,
            ).exclude(pk=self.pk).exists()
            if pending_invite_exists:
                errors["sent_to"] = "Ja existe convite pendente para este grupo."

        if errors:
            raise ValidationError(errors)

    def accept(self):
        self._respond(self.InviteStatus.ACCEPTED)

    def decline(self):
        self._respond(self.InviteStatus.DECLINED)

    def cancel(self):
        self._respond(self.InviteStatus.CANCELED)

    def _respond(self, status):
        if self.status != self.InviteStatus.PENDING:
            raise ValidationError("Apenas convites pendentes podem ser respondidos.")

        self.status = status
        self.responded_at = timezone.now()
        self.save(update_fields=["status", "responded_at"])

    def __str__(self):
        return (
            f"GroupInvite(group_id={self.group_id}, "
            f"sent_to_id={self.sent_to_id}, status={self.status})"
        )
