import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


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
