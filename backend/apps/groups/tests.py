from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import (
    PermissionDenied as DRFPermissionDenied,
    ValidationError as DRFValidationError,
)
from rest_framework import status
from rest_framework.test import APITestCase

from apps.groups.commands import (
    AcceptGroupInviteCommand,
    CancelGroupInviteCommand,
    DeclineGroupInviteCommand,
)
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


class GroupInviteCommandTests(TestCase):
    def create_user(self, email):
        return User.objects.create_user(
            email=email,
            password="12345678",
            full_name="Test User",
        )

    def create_group(self):
        return StudyGroup.objects.create(
            name="Grupo de estudos",
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

    def test_accept_command_accepts_pending_invite_and_creates_membership(self):
        invite = self.create_invite()

        result = AcceptGroupInviteCommand(
            invite=invite,
            actor=invite.sent_to,
        ).execute()

        result.refresh_from_db()
        self.assertEqual(result.status, GroupInvite.InviteStatus.ACCEPTED)
        self.assertIsNotNone(result.responded_at)
        membership = GroupMembership.objects.get(
            user=invite.sent_to,
            group=invite.group,
        )
        self.assertTrue(membership.is_active)
        self.assertEqual(membership.role, GroupMembership.MembershipRole.MEMBER)

    def test_accept_command_reactivates_existing_membership(self):
        invite = self.create_invite()
        membership = GroupMembership.objects.create(
            user=invite.sent_to,
            group=invite.group,
            role=GroupMembership.MembershipRole.OWNER,
            is_active=False,
        )

        AcceptGroupInviteCommand(invite=invite, actor=invite.sent_to).execute()

        membership.refresh_from_db()
        self.assertTrue(membership.is_active)
        self.assertEqual(membership.role, GroupMembership.MembershipRole.MEMBER)

    def test_decline_command_declines_pending_invite(self):
        invite = self.create_invite()

        result = DeclineGroupInviteCommand(
            invite=invite,
            actor=invite.sent_to,
        ).execute()

        result.refresh_from_db()
        self.assertEqual(result.status, GroupInvite.InviteStatus.DECLINED)
        self.assertIsNotNone(result.responded_at)

    def test_cancel_command_cancels_pending_invite(self):
        invite = self.create_invite()

        result = CancelGroupInviteCommand(
            invite=invite,
            actor=invite.sent_by,
        ).execute()

        result.refresh_from_db()
        self.assertEqual(result.status, GroupInvite.InviteStatus.CANCELED)
        self.assertIsNotNone(result.responded_at)

    def test_command_blocks_non_pending_invite(self):
        invite = self.create_invite(
            status=GroupInvite.InviteStatus.DECLINED,
            responded_at=timezone.now(),
        )

        with self.assertRaises(DRFValidationError):
            AcceptGroupInviteCommand(invite=invite, actor=invite.sent_to).execute()

    def test_accept_and_decline_commands_block_wrong_actor(self):
        invite = self.create_invite()
        other_user = self.create_user("other@example.com")

        with self.assertRaises(DRFPermissionDenied):
            AcceptGroupInviteCommand(invite=invite, actor=other_user).execute()

        with self.assertRaises(DRFPermissionDenied):
            DeclineGroupInviteCommand(invite=invite, actor=other_user).execute()

    def test_cancel_command_blocks_wrong_actor(self):
        invite = self.create_invite()

        with self.assertRaises(DRFPermissionDenied):
            CancelGroupInviteCommand(invite=invite, actor=invite.sent_to).execute()


class StudyGroupApiTests(APITestCase):
    def create_user(self, email):
        return User.objects.create_user(
            email=email,
            password="12345678",
            full_name="Test User",
        )

    def create_group_with_membership(
        self,
        user,
        role=GroupMembership.MembershipRole.MEMBER,
        is_active=True,
    ):
        group = StudyGroup.objects.create(
            name="Grupo de estudos",
            description="Grupo para testes.",
        )
        GroupMembership.objects.create(
            user=user,
            group=group,
            role=role,
            is_active=is_active,
        )
        return group

    def test_authenticated_user_can_create_group(self):
        user = self.create_user("owner@example.com")
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/groups/",
            {
                "name": "Grupo de estudos",
                "description": "Grupo para testes.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        group = StudyGroup.objects.get(id=response.data["id"])
        membership = GroupMembership.objects.get(user=user, group=group)

        self.assertEqual(group.name, "Grupo de estudos")
        self.assertEqual(membership.role, GroupMembership.MembershipRole.OWNER)
        self.assertTrue(membership.is_active)
        self.assertEqual(membership.group_points, 0)

    def test_create_group_does_not_accept_membership_role_in_payload(self):
        user = self.create_user("owner@example.com")
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/groups/",
            {
                "name": "Grupo de estudos",
                "description": "Grupo para testes.",
                "role": GroupMembership.MembershipRole.MEMBER,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        group = StudyGroup.objects.get(id=response.data["id"])
        membership = GroupMembership.objects.get(user=user, group=group)

        self.assertEqual(membership.role, GroupMembership.MembershipRole.OWNER)
        self.assertNotIn("role", response.data)

    def test_unauthenticated_user_cannot_create_group(self):
        response = self.client.post(
            "/api/groups/",
            {
                "name": "Grupo de estudos",
                "description": "Grupo para testes.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_group_creation_rolls_back_if_membership_creation_fails(self):
        from unittest.mock import patch

        user = self.create_user("owner@example.com")
        self.client.force_authenticate(user=user)

        with patch("apps.groups.views.GroupMembership.objects.create") as mock_create:
            mock_create.side_effect = IntegrityError("forced failure")

            with self.assertRaises(IntegrityError):
                self.client.post(
                    "/api/groups/",
                    {
                        "name": "Grupo de estudos",
                        "description": "Grupo para testes.",
                    },
                    format="json",
                )

        self.assertFalse(StudyGroup.objects.filter(name="Grupo de estudos").exists())

    def test_owner_can_update_group(self):
        owner = self.create_user("owner@example.com")
        group = self.create_group_with_membership(
            owner,
            role=GroupMembership.MembershipRole.OWNER,
        )
        self.client.force_authenticate(user=owner)

        response = self.client.put(
            f"/api/groups/{group.id}/",
            {
                "name": "Grupo atualizado",
                "description": "Descricao atualizada.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        group.refresh_from_db()
        self.assertEqual(group.name, "Grupo atualizado")
        self.assertEqual(group.description, "Descricao atualizada.")

    def test_active_member_cannot_update_group(self):
        member = self.create_user("member@example.com")
        group = self.create_group_with_membership(
            member,
            role=GroupMembership.MembershipRole.MEMBER,
        )
        self.client.force_authenticate(user=member)

        response = self.client.put(
            f"/api/groups/{group.id}/",
            {
                "name": "Tentativa de atualizacao",
                "description": "Nao deve persistir.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        group.refresh_from_db()
        self.assertEqual(group.name, "Grupo de estudos")

    def test_active_member_cannot_patch_group(self):
        member = self.create_user("member@example.com")
        group = self.create_group_with_membership(
            member,
            role=GroupMembership.MembershipRole.MEMBER,
        )
        self.client.force_authenticate(user=member)

        response = self.client.patch(
            f"/api/groups/{group.id}/",
            {"name": "Tentativa parcial"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        group.refresh_from_db()
        self.assertEqual(group.name, "Grupo de estudos")

    def test_authenticated_non_member_cannot_update_group(self):
        owner = self.create_user("owner@example.com")
        outsider = self.create_user("outsider@example.com")
        group = self.create_group_with_membership(
            owner,
            role=GroupMembership.MembershipRole.OWNER,
        )
        self.client.force_authenticate(user=outsider)

        response = self.client.put(
            f"/api/groups/{group.id}/",
            {
                "name": "Tentativa de outsider",
                "description": "Nao deve persistir.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        group.refresh_from_db()
        self.assertEqual(group.name, "Grupo de estudos")

    def test_inactive_owner_cannot_update_group(self):
        owner = self.create_user("owner@example.com")
        group = self.create_group_with_membership(
            owner,
            role=GroupMembership.MembershipRole.OWNER,
            is_active=False,
        )
        self.client.force_authenticate(user=owner)

        response = self.client.put(
            f"/api/groups/{group.id}/",
            {
                "name": "Tentativa inativa",
                "description": "Nao deve persistir.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        group.refresh_from_db()
        self.assertEqual(group.name, "Grupo de estudos")

    def test_authenticated_user_can_retrieve_group_detail(self):
        owner = self.create_user("owner@example.com")
        viewer = self.create_user("viewer@example.com")
        group = self.create_group_with_membership(
            owner,
            role=GroupMembership.MembershipRole.OWNER,
        )
        self.client.force_authenticate(user=viewer)

        response = self.client.get(f"/api/groups/{group.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(group.id))


class GroupInviteApiTests(APITestCase):
    def create_user(self, email):
        return User.objects.create_user(
            email=email,
            password="12345678",
            full_name="Test User",
        )

    def create_group_with_owner(self, owner_email="owner@example.com"):
        owner = self.create_user(owner_email)
        group = StudyGroup.objects.create(
            name="Grupo de estudos",
            description="Grupo para testes.",
        )
        GroupMembership.objects.create(
            user=owner,
            group=group,
            role=GroupMembership.MembershipRole.OWNER,
        )
        return owner, group

    def test_owner_can_create_invite(self):
        owner, group = self.create_group_with_owner()
        recipient = self.create_user("member@example.com")
        self.client.force_authenticate(user=owner)

        response = self.client.post(
            "/api/groups/invites/",
            {
                "group": str(group.id),
                "sent_to_email": recipient.email,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["sent_by"], owner.id)
        self.assertEqual(response.data["sent_to"], recipient.id)
        self.assertEqual(response.data["group"], group.id)
        self.assertEqual(response.data["status"], GroupInvite.InviteStatus.PENDING)

    def test_non_owner_cannot_create_invite(self):
        owner, group = self.create_group_with_owner()
        member = self.create_user("member@example.com")
        GroupMembership.objects.create(user=member, group=group)
        recipient = self.create_user("destinatario@example.com")
        self.client.force_authenticate(user=member)

        response = self.client.post(
            "/api/groups/invites/",
            {
                "group": str(group.id),
                "sent_to_email": recipient.email,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_invite_rejects_unknown_email(self):
        owner, group = self.create_group_with_owner()
        self.client.force_authenticate(user=owner)

        response = self.client.post(
            "/api/groups/invites/",
            {
                "group": str(group.id),
                "sent_to_email": "missing@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recipient_can_accept_invite_and_create_membership(self):
        owner, group = self.create_group_with_owner()
        recipient = self.create_user("member@example.com")
        invite = GroupInvite.objects.create(
            group=group,
            sent_by=owner,
            sent_to=recipient,
        )
        self.client.force_authenticate(user=recipient)

        response = self.client.post(f"/api/groups/invites/{invite.id}/accept/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invite.refresh_from_db()
        self.assertEqual(invite.status, GroupInvite.InviteStatus.ACCEPTED)
        self.assertIsNotNone(invite.responded_at)
        membership = GroupMembership.objects.get(user=recipient, group=group)
        self.assertTrue(membership.is_active)

    def test_pending_invites_list_only_returns_recipient_invites(self):
        owner, group = self.create_group_with_owner()
        recipient = self.create_user("member@example.com")
        other_user = self.create_user("outra@example.com")
        GroupInvite.objects.create(group=group, sent_by=owner, sent_to=recipient)
        GroupInvite.objects.create(group=group, sent_by=owner, sent_to=other_user)
        self.client.force_authenticate(user=recipient)

        response = self.client.get("/api/groups/invites/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["sent_to"], recipient.id)


class GroupMembershipApiTests(APITestCase):
    def create_user(self, email):
        return User.objects.create_user(
            email=email,
            password="12345678",
            full_name="Test User",
        )

    def create_group_with_members(self):
        owner = self.create_user("owner@example.com")
        member = self.create_user("member@example.com")
        other = self.create_user("other@example.com")
        group = StudyGroup.objects.create(
            name="Grupo de estudos",
            description="Grupo para testes.",
        )
        owner_membership = GroupMembership.objects.create(
            user=owner,
            group=group,
            role=GroupMembership.MembershipRole.OWNER,
            group_points=50,
        )
        member_membership = GroupMembership.objects.create(
            user=member,
            group=group,
            role=GroupMembership.MembershipRole.MEMBER,
            group_points=30,
        )
        GroupMembership.objects.create(user=other, group=group, group_points=10)
        return group, owner_membership, member_membership, owner, member

    def test_member_can_list_group_members(self):
        group, owner_membership, member_membership, owner, member = (
            self.create_group_with_members()
        )
        self.client.force_authenticate(user=member)

        response = self.client.get(f"/api/groups/{group.id}/members/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.data[0]["group_points"], 50)

    def test_non_member_cannot_list_group_members(self):
        group, owner_membership, member_membership, owner, member = (
            self.create_group_with_members()
        )
        outsider = self.create_user("outsider@example.com")
        self.client.force_authenticate(user=outsider)

        response = self.client.get(f"/api/groups/{group.id}/members/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_can_leave_group_but_owner_cannot(self):
        group, owner_membership, member_membership, owner, member = (
            self.create_group_with_members()
        )
        self.client.force_authenticate(user=member)

        response = self.client.delete(
            f"/api/groups/{group.id}/members/{member_membership.id}/leave/"
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        member_membership.refresh_from_db()
        self.assertFalse(member_membership.is_active)

        self.client.force_authenticate(user=owner)
        response = self.client.delete(
            f"/api/groups/{group.id}/members/{owner_membership.id}/leave/"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GroupRankingApiTests(APITestCase):
    def create_user(self, email):
        return User.objects.create_user(
            email=email,
            password="12345678",
            full_name="Test User",
        )

    def test_ranking_is_public_and_ordered_by_points(self):
        group = StudyGroup.objects.create(
            name="Grupo de estudos",
            description="Grupo para testes.",
        )
        first = self.create_user("first@example.com")
        second = self.create_user("second@example.com")
        GroupMembership.objects.create(
            user=first,
            group=group,
            group_points=30,
        )
        GroupMembership.objects.create(
            user=second,
            group=group,
            group_points=60,
        )

        response = self.client.get(f"/api/groups/{group.id}/ranking/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["rank"], 1)
        self.assertEqual(response.data[0]["user_id"], str(second.id))
        self.assertEqual(response.data[1]["rank"], 2)
