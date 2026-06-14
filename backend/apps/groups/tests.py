from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from apps.groups.models import GroupMembership, StudyGroup


User = get_user_model()


class GroupMembershipModelTests(TestCase):
    def create_user(self, email):
        return User.objects.create_user(
            email=email,
            password="12345678",
            full_name="Test User",
        )

    def create_group(self, name="Grupo de estudos"):
        return StudyGroup.objects.create(
            name=name,
            description="Grupo para testes.",
        )

    def test_create_membership_between_user_and_group(self):
        user = self.create_user("ana@example.com")
        group = self.create_group()

        membership = GroupMembership.objects.create(user=user, group=group)

        self.assertEqual(membership.user, user)
        self.assertEqual(membership.group, group)
        self.assertEqual(membership.role, GroupMembership.MembershipRole.MEMBER)
        self.assertEqual(membership.group_points, 0)
        self.assertTrue(membership.is_active)
        self.assertIsNotNone(membership.joined_at)

    def test_user_group_membership_must_be_unique(self):
        user = self.create_user("ana@example.com")
        group = self.create_group()
        GroupMembership.objects.create(user=user, group=group)

        with self.assertRaises(IntegrityError):
            GroupMembership.objects.create(user=user, group=group)

    def test_group_points_cannot_be_negative(self):
        user = self.create_user("ana@example.com")
        group = self.create_group()
        membership = GroupMembership(
            user=user,
            group=group,
            group_points=-1,
        )

        with self.assertRaises(ValidationError):
            membership.full_clean()

    def test_membership_roles_are_validated(self):
        user = self.create_user("ana@example.com")
        group = self.create_group()
        owner_membership = GroupMembership(
            user=user,
            group=group,
            role=GroupMembership.MembershipRole.OWNER,
        )
        owner_membership.full_clean()

        invalid_membership = GroupMembership(
            user=user,
            group=group,
            role="INVALID",
        )

        with self.assertRaises(ValidationError):
            invalid_membership.full_clean()

    def test_rank_is_derived_from_active_memberships_in_same_group(self):
        group = self.create_group()
        first_user = self.create_user("ana@example.com")
        second_user = self.create_user("bia@example.com")
        third_user = self.create_user("caio@example.com")

        first_membership = GroupMembership.objects.create(
            user=first_user,
            group=group,
            group_points=40,
        )
        second_membership = GroupMembership.objects.create(
            user=second_user,
            group=group,
            group_points=80,
        )
        third_membership = GroupMembership.objects.create(
            user=third_user,
            group=group,
            group_points=80,
        )

        self.assertEqual(second_membership.rank, 1)
        self.assertEqual(third_membership.rank, 1)
        self.assertEqual(first_membership.rank, 3)
