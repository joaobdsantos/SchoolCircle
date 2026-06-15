from datetime import date
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.attendance.models import AttendanceRecord
from apps.gamification.models import PointTransaction, UserProgress
from apps.groups.models import StudyGroup
from apps.study.models import StudySession

User = get_user_model()


class UserProgressModelTests(APITestCase):
    def create_user(self, email="ana@example.com"):
        return User.objects.create_user(
            email=email,
            password="12345678",
            full_name="Ana Silva",
        )

    def test_create_user_progress_for_user(self):
        user = self.create_user()
        progress = UserProgress.objects.get(user=user)

        self.assertIsNotNone(progress.id)
        self.assertEqual(progress.current_streak, 0)
        self.assertEqual(progress.longest_streak, 0)
        self.assertEqual(progress.total_points, 0)
        self.assertIsNone(progress.last_valid_activity_date)

    def test_block_second_user_progress_for_same_user(self):
        user = self.create_user()
        UserProgress.objects.get(user=user)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                UserProgress.objects.create(user=user)

    def test_total_points_cannot_be_negative(self):
        user = self.create_user("outro@example.com")
        progress = UserProgress.objects.get(user=user)
        progress.total_points = -1

        with self.assertRaises(ValidationError):
            progress.full_clean()

    def test_current_streak_cannot_be_negative(self):
        user = self.create_user("novo@example.com")
        progress = UserProgress.objects.get(user=user)
        progress.current_streak = -1

        with self.assertRaises(ValidationError):
            progress.full_clean()

    def test_longest_streak_cannot_be_negative(self):
        user = self.create_user("mais-um@example.com")
        progress = UserProgress.objects.get(user=user)
        progress.longest_streak = -1

        with self.assertRaises(ValidationError):
            progress.full_clean()

    def test_longest_streak_cannot_be_smaller_than_current(self):
        user = self.create_user("streak@example.com")
        progress = UserProgress.objects.get(user=user)
        progress.current_streak = 3
        progress.longest_streak = 2

        with self.assertRaises(ValidationError):
            progress.full_clean()

    def test_add_points_sums_points_correctly(self):
        progress = UserProgress.objects.get(user=self.create_user())

        progress.add_points(7)
        progress.refresh_from_db()

        self.assertEqual(progress.total_points, 7)

    def test_add_points_blocks_negative_values(self):
        progress = UserProgress.objects.get(user=self.create_user())

        with self.assertRaises(ValidationError):
            progress.add_points(-1)

    def test_reset_streak_zeros_current_streak(self):
        progress = UserProgress.objects.get(user=self.create_user())
        progress.current_streak = 4
        progress.longest_streak = 4
        progress.save(update_fields=["current_streak", "longest_streak"])

        progress.reset_streak()
        progress.refresh_from_db()

        self.assertEqual(progress.current_streak, 0)
        self.assertEqual(progress.longest_streak, 4)

    def test_update_streak_updates_streak_fields(self):
        progress = UserProgress.objects.get(user=self.create_user())

        progress.update_streak(date(2026, 6, 14))
        progress.refresh_from_db()
        self.assertEqual(progress.current_streak, 1)
        self.assertEqual(progress.longest_streak, 1)
        self.assertEqual(progress.last_valid_activity_date, date(2026, 6, 14))

        progress.update_streak(date(2026, 6, 15))
        progress.refresh_from_db()
        self.assertEqual(progress.current_streak, 2)
        self.assertEqual(progress.longest_streak, 2)
        self.assertEqual(progress.last_valid_activity_date, date(2026, 6, 15))

    def test_update_streak_ignores_older_activity_date(self):
        progress = UserProgress.objects.get(user=self.create_user())

        progress.update_streak(date(2026, 6, 15))
        progress.refresh_from_db()

        self.assertEqual(progress.current_streak, 1)
        self.assertEqual(progress.longest_streak, 1)
        self.assertEqual(progress.last_valid_activity_date, date(2026, 6, 15))

        progress.update_streak(date(2026, 6, 14))
        progress.refresh_from_db()

        self.assertEqual(progress.current_streak, 1)
        self.assertEqual(progress.longest_streak, 1)
        self.assertEqual(progress.last_valid_activity_date, date(2026, 6, 15))

    def test_update_streak_ignores_same_activity_date(self):
        progress = UserProgress.objects.get(user=self.create_user())

        progress.update_streak(date(2026, 6, 14))
        progress.refresh_from_db()
        self.assertEqual(progress.current_streak, 1)
        self.assertEqual(progress.longest_streak, 1)
        self.assertEqual(progress.last_valid_activity_date, date(2026, 6, 14))

        progress.update_streak(date(2026, 6, 14))
        progress.refresh_from_db()

        self.assertEqual(progress.current_streak, 1)
        self.assertEqual(progress.longest_streak, 1)
        self.assertEqual(progress.last_valid_activity_date, date(2026, 6, 14))

        progress.update_streak(date(2026, 6, 14))
        progress.refresh_from_db()

        self.assertEqual(progress.current_streak, 1)
        self.assertEqual(progress.longest_streak, 1)
        self.assertEqual(progress.last_valid_activity_date, date(2026, 6, 14))


class UserProgressApiTests(APITestCase):
    def create_user(self, email="ana@example.com"):
        return User.objects.create_user(
            email=email,
            password="12345678",
            full_name="Ana Silva",
        )

    def test_get_returns_only_authenticated_user_progress(self):
        user_one = self.create_user("ana@example.com")
        user_two = self.create_user("bia@example.com")
        self.client.force_authenticate(user=user_one)
        progress_one = UserProgress.objects.get(user=user_one)
        UserProgress.objects.get(user=user_two)
        progress_one.total_points = 12
        progress_one.current_streak = 3
        progress_one.longest_streak = 5
        progress_one.save(
            update_fields=["total_points", "current_streak", "longest_streak"]
        )

        response = self.client.get("/api/user-progress/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_points"], 12)
        self.assertEqual(response.data["current_streak"], 3)
        self.assertEqual(response.data["longest_streak"], 5)


class PointTransactionModelTests(APITestCase):
    def create_user(self, email="ana@example.com"):
        return User.objects.create_user(
            email=email,
            password="12345678",
            full_name="Ana Silva",
        )

    def create_group(self, name="Grupo de estudos"):
        return StudyGroup.objects.create(
            name=name,
            description="Grupo para testes.",
        )

    def create_attendance_record(self, user):
        return AttendanceRecord.objects.create(
            user=user,
            class_date=date(2026, 6, 14),
            period=AttendanceRecord.Period.MORNING,
            photo_url="https://example.com/attendance.jpg",
        )

    def create_study_session(self, user):
        return StudySession.objects.create(
            user=user,
            study_date=date(2026, 6, 14),
            content_description="Estudo de grafos e Dijkstra",
            photo_url="https://example.com/study.jpg",
        )

    def test_create_attendance_point_transaction(self):
        user = self.create_user()
        attendance = self.create_attendance_record(user)

        transaction_obj = PointTransaction(
            user=user,
            points=10,
            reason="Presenca registrada.",
            source_type=PointTransaction.ActivityType.ATTENDANCE,
            attendance_record=attendance,
        )
        transaction_obj.full_clean()
        transaction_obj.save()

        self.assertTrue(transaction_obj.is_from_attendance())
        self.assertFalse(transaction_obj.is_from_study_session())
        self.assertFalse(transaction_obj.is_group_scoped())

    def test_create_study_session_point_transaction(self):
        user = self.create_user()
        study_session = self.create_study_session(user)

        transaction_obj = PointTransaction(
            user=user,
            points=15,
            reason="Sessao de estudo concluida.",
            source_type=PointTransaction.ActivityType.STUDY_SESSION,
            study_session=study_session,
        )
        transaction_obj.full_clean()
        transaction_obj.save()

        self.assertTrue(transaction_obj.is_from_study_session())
        self.assertFalse(transaction_obj.is_from_attendance())

    def test_create_group_scoped_point_transaction(self):
        user = self.create_user()
        attendance = self.create_attendance_record(user)
        group = self.create_group()

        transaction_obj = PointTransaction(
            user=user,
            points=20,
            reason="Participacao em grupo.",
            source_type=PointTransaction.ActivityType.ATTENDANCE,
            attendance_record=attendance,
            study_group=group,
        )
        transaction_obj.full_clean()
        transaction_obj.save()

        self.assertTrue(transaction_obj.is_group_scoped())
        self.assertEqual(transaction_obj.study_group, group)

    def test_points_cannot_be_zero(self):
        user = self.create_user()
        attendance = self.create_attendance_record(user)
        transaction_obj = PointTransaction(
            user=user,
            points=0,
            reason="Zero nao vale.",
            source_type=PointTransaction.ActivityType.ATTENDANCE,
            attendance_record=attendance,
        )

        with self.assertRaises(ValidationError):
            transaction_obj.full_clean()

    def test_reason_cannot_be_empty(self):
        user = self.create_user()
        attendance = self.create_attendance_record(user)
        transaction_obj = PointTransaction(
            user=user,
            points=10,
            reason="",
            source_type=PointTransaction.ActivityType.ATTENDANCE,
            attendance_record=attendance,
        )

        with self.assertRaises(ValidationError):
            transaction_obj.full_clean()

    def test_attendance_source_requires_attendance_record(self):
        user = self.create_user()
        transaction_obj = PointTransaction(
            user=user,
            points=10,
            reason="Presenca sem registro.",
            source_type=PointTransaction.ActivityType.ATTENDANCE,
        )

        with self.assertRaises(ValidationError):
            transaction_obj.full_clean()

    def test_study_session_source_requires_study_session(self):
        user = self.create_user()
        transaction_obj = PointTransaction(
            user=user,
            points=10,
            reason="Sessao sem registro.",
            source_type=PointTransaction.ActivityType.STUDY_SESSION,
        )

        with self.assertRaises(ValidationError):
            transaction_obj.full_clean()

    def test_attendance_and_study_session_cannot_be_set_together(self):
        user = self.create_user()
        attendance = self.create_attendance_record(user)
        study_session = self.create_study_session(user)
        transaction_obj = PointTransaction(
            user=user,
            points=10,
            reason="Campos conflitantes.",
            source_type=PointTransaction.ActivityType.ATTENDANCE,
            attendance_record=attendance,
            study_session=study_session,
        )

        with self.assertRaises(ValidationError):
            transaction_obj.full_clean()

    def test_get_returns_only_authenticated_user_transactions(self):
        user_one = self.create_user("ana@example.com")
        user_two = self.create_user("bia@example.com")
        attendance_one = self.create_attendance_record(user_one)
        attendance_two = self.create_attendance_record(user_two)
        self.client.force_authenticate(user=user_one)

        tx_one = PointTransaction.objects.create(
            user=user_one,
            points=10,
            reason="Usuario 1.",
            source_type=PointTransaction.ActivityType.ATTENDANCE,
            attendance_record=attendance_one,
        )
        tx_two = PointTransaction.objects.create(
            user=user_two,
            points=12,
            reason="Usuario 2.",
            source_type=PointTransaction.ActivityType.ATTENDANCE,
            attendance_record=attendance_two,
        )

        PointTransaction.objects.filter(id=tx_one.id).update(
            created_at=timezone.now() - timedelta(days=1)
        )
        PointTransaction.objects.filter(id=tx_two.id).update(
            created_at=timezone.now()
        )

        response = self.client.get("/api/point-transactions/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["reason"], "Usuario 1.")

    def test_get_returns_ordered_by_created_at_desc(self):
        user = self.create_user()
        attendance_one = self.create_attendance_record(user)
        attendance_two = AttendanceRecord.objects.create(
            user=user,
            class_date=date(2026, 6, 15),
            period=AttendanceRecord.Period.AFTERNOON,
            photo_url="https://example.com/attendance-2.jpg",
        )
        self.client.force_authenticate(user=user)

        older_tx = PointTransaction.objects.create(
            user=user,
            points=10,
            reason="Antiga.",
            source_type=PointTransaction.ActivityType.ATTENDANCE,
            attendance_record=attendance_one,
        )
        newer_tx = PointTransaction.objects.create(
            user=user,
            points=12,
            reason="Nova.",
            source_type=PointTransaction.ActivityType.ATTENDANCE,
            attendance_record=attendance_two,
        )

        PointTransaction.objects.filter(id=older_tx.id).update(
            created_at=timezone.now() - timedelta(days=1)
        )
        PointTransaction.objects.filter(id=newer_tx.id).update(
            created_at=timezone.now()
        )

        response = self.client.get("/api/point-transactions/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["reason"], "Nova.")
        self.assertEqual(response.data[1]["reason"], "Antiga.")
