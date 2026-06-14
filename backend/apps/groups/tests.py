from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from apps.groups.models import GroupInvite, GroupMembership, StudyGroup


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


class GroupInviteModelTests(TestCase):
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

    def create_invite(self, group=None, sent_by=None, sent_to=None, **extra_fields):
        group = group or self.create_group()
        sent_by = sent_by or self.create_user("owner@example.com")
        sent_to = sent_to or self.create_user("member@example.com")
        return GroupInvite.objects.create(
            group=group,
            sent_by=sent_by,
            sent_to=sent_to,
            **extra_fields,
        )

    def test_create_pending_invite(self):
        group = self.create_group()
        sent_by = self.create_user("owner@example.com")
        sent_to = self.create_user("member@example.com")

        invite = GroupInvite.objects.create(
            group=group,
            sent_by=sent_by,
            sent_to=sent_to,
        )

        self.assertEqual(invite.group, group)
        self.assertEqual(invite.sent_by, sent_by)
        self.assertEqual(invite.sent_to, sent_to)
        self.assertEqual(invite.status, GroupInvite.InviteStatus.PENDING)
        self.assertIsNotNone(invite.sent_at)
        self.assertIsNone(invite.responded_at)

    def test_invite_cannot_be_sent_to_self(self):
        user = self.create_user("ana@example.com")
        invite = GroupInvite(
            group=self.create_group(),
            sent_by=user,
            sent_to=user,
        )

        with self.assertRaises(ValidationError):
            invite.full_clean()

    def test_pending_invite_must_be_unique_for_group_and_recipient(self):
        group = self.create_group()
        sent_by = self.create_user("owner@example.com")
        sent_to = self.create_user("member@example.com")
        self.create_invite(group=group, sent_by=sent_by, sent_to=sent_to)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_invite(group=group, sent_by=sent_by, sent_to=sent_to)

    def test_new_invite_is_allowed_when_previous_invite_is_not_pending(self):
        group = self.create_group()
        sent_by = self.create_user("owner@example.com")
        sent_to = self.create_user("member@example.com")
        self.create_invite(
            group=group,
            sent_by=sent_by,
            sent_to=sent_to,
            status=GroupInvite.InviteStatus.DECLINED,
            responded_at=timezone.now(),
        )

        invite = self.create_invite(group=group, sent_by=sent_by, sent_to=sent_to)

        self.assertEqual(invite.status, GroupInvite.InviteStatus.PENDING)

    def test_invite_cannot_target_active_group_member(self):
        group = self.create_group()
        sent_by = self.create_user("owner@example.com")
        sent_to = self.create_user("member@example.com")
        GroupMembership.objects.create(group=group, user=sent_to)
        invite = GroupInvite(group=group, sent_by=sent_by, sent_to=sent_to)

        with self.assertRaises(ValidationError):
            invite.full_clean()

    def test_accept_sets_status_and_responded_at(self):
        invite = self.create_invite()

        invite.accept()
        invite.refresh_from_db()

        self.assertEqual(invite.status, GroupInvite.InviteStatus.ACCEPTED)
        self.assertIsNotNone(invite.responded_at)

    def test_decline_sets_status_and_responded_at(self):
        invite = self.create_invite()

        invite.decline()
        invite.refresh_from_db()

        self.assertEqual(invite.status, GroupInvite.InviteStatus.DECLINED)
        self.assertIsNotNone(invite.responded_at)

    def test_cancel_sets_status_and_responded_at(self):
        invite = self.create_invite()

        invite.cancel()
        invite.refresh_from_db()

        self.assertEqual(invite.status, GroupInvite.InviteStatus.CANCELED)
        self.assertIsNotNone(invite.responded_at)

    def test_invite_cannot_be_responded_twice(self):
        invite = self.create_invite()
        invite.accept()

        with self.assertRaises(ValidationError):
            invite.decline()

    def test_responded_at_matches_status(self):
        pending_with_response = GroupInvite(
            group=self.create_group("Grupo 1"),
            sent_by=self.create_user("owner@example.com"),
            sent_to=self.create_user("member@example.com"),
            responded_at=timezone.now(),
        )

        with self.assertRaises(ValidationError):
            pending_with_response.full_clean()

        accepted_without_response = GroupInvite(
            group=self.create_group("Grupo 2"),
            sent_by=self.create_user("owner2@example.com"),
            sent_to=self.create_user("member2@example.com"),
            status=GroupInvite.InviteStatus.ACCEPTED,
        )

        with self.assertRaises(ValidationError):
            accepted_without_response.full_clean()
