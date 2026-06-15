from datetime import date

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.attendance.models import AttendanceRecord
from apps.gamification.models import PointTransaction, UserProgress
from apps.gamification.services import PointsService
from apps.gamification.strategies import (
    AttendancePointsStrategy,
    StudySessionPointsStrategy,
)
from apps.groups.models import StudyGroup
from apps.study.models import StudySession


User = get_user_model()


class PointsServiceTests(APITestCase):
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

    def create_attendance_record(self, user, **extra_fields):
        data = {
            "user": user,
            "class_date": date(2026, 6, 14),
            "period": AttendanceRecord.Period.MORNING,
            "photo_url": "https://example.com/attendance.jpg",
            **extra_fields,
        }
        return AttendanceRecord.objects.create(**data)

    def create_study_session(self, user, **extra_fields):
        data = {
            "user": user,
            "study_date": date(2026, 6, 14),
            "content_description": "Estudo de grafos e Dijkstra",
            "photo_url": "https://example.com/study.jpg",
            **extra_fields,
        }
        return StudySession.objects.create(**data)

    def test_grant_points_creates_attendance_transaction(self):
        user = self.create_user()
        attendance = self.create_attendance_record(user)

        point_transaction = PointsService.grant_points(
            user=user,
            activity=attendance,
            strategy=AttendancePointsStrategy(),
        )

        self.assertIsNotNone(point_transaction)
        self.assertEqual(point_transaction.user, user)
        self.assertEqual(point_transaction.attendance_record, attendance)
        self.assertIsNone(point_transaction.study_session)
        self.assertEqual(
            point_transaction.source_type,
            PointTransaction.ActivityType.ATTENDANCE,
        )

    def test_grant_points_updates_total_points_for_attendance(self):
        user = self.create_user()
        attendance = self.create_attendance_record(user, points_granted=10)

        PointsService.grant_points(
            user=user,
            activity=attendance,
            strategy=AttendancePointsStrategy(),
        )
        progress = UserProgress.objects.get(user=user)

        self.assertEqual(progress.total_points, 10)

    def test_grant_points_updates_streak_for_attendance(self):
        user = self.create_user()
        attendance = self.create_attendance_record(
            user,
            class_date=date(2026, 6, 14),
        )

        PointsService.grant_points(
            user=user,
            activity=attendance,
            strategy=AttendancePointsStrategy(),
        )
        progress = UserProgress.objects.get(user=user)

        self.assertEqual(progress.current_streak, 1)
        self.assertEqual(progress.longest_streak, 1)
        self.assertEqual(progress.last_valid_activity_date, date(2026, 6, 14))

    def test_grant_points_creates_study_session_transaction(self):
        user = self.create_user()
        study_session = self.create_study_session(user)

        point_transaction = PointsService.grant_points(
            user=user,
            activity=study_session,
            strategy=StudySessionPointsStrategy(),
        )

        self.assertIsNotNone(point_transaction)
        self.assertEqual(point_transaction.user, user)
        self.assertEqual(point_transaction.study_session, study_session)
        self.assertIsNone(point_transaction.attendance_record)
        self.assertEqual(
            point_transaction.source_type,
            PointTransaction.ActivityType.STUDY_SESSION,
        )

    def test_grant_points_updates_total_points_for_study_session(self):
        user = self.create_user()
        study_session = self.create_study_session(user, points_granted=5)

        PointsService.grant_points(
            user=user,
            activity=study_session,
            strategy=StudySessionPointsStrategy(),
        )
        progress = UserProgress.objects.get(user=user)

        self.assertEqual(progress.total_points, 5)

    def test_grant_points_updates_streak_for_study_session(self):
        user = self.create_user()
        study_session = self.create_study_session(
            user,
            study_date=date(2026, 6, 14),
        )

        PointsService.grant_points(
            user=user,
            activity=study_session,
            strategy=StudySessionPointsStrategy(),
        )
        progress = UserProgress.objects.get(user=user)

        self.assertEqual(progress.current_streak, 1)
        self.assertEqual(progress.longest_streak, 1)
        self.assertEqual(progress.last_valid_activity_date, date(2026, 6, 14))

    def test_grant_points_does_not_duplicate_attendance_transaction(self):
        user = self.create_user()
        attendance = self.create_attendance_record(user, points_granted=10)

        first_transaction = PointsService.grant_points(
            user=user,
            activity=attendance,
            strategy=AttendancePointsStrategy(),
        )
        second_transaction = PointsService.grant_points(
            user=user,
            activity=attendance,
            strategy=AttendancePointsStrategy(),
        )

        self.assertEqual(first_transaction, second_transaction)
        self.assertEqual(
            PointTransaction.objects.filter(attendance_record=attendance).count(),
            1,
        )

    def test_grant_points_does_not_duplicate_study_session_transaction(self):
        user = self.create_user()
        study_session = self.create_study_session(user, points_granted=5)

        first_transaction = PointsService.grant_points(
            user=user,
            activity=study_session,
            strategy=StudySessionPointsStrategy(),
        )
        second_transaction = PointsService.grant_points(
            user=user,
            activity=study_session,
            strategy=StudySessionPointsStrategy(),
        )

        self.assertEqual(first_transaction, second_transaction)
        self.assertEqual(
            PointTransaction.objects.filter(study_session=study_session).count(),
            1,
        )

    def test_repeated_grant_does_not_add_points_twice(self):
        user = self.create_user()
        attendance = self.create_attendance_record(user, points_granted=10)

        PointsService.grant_points(
            user=user,
            activity=attendance,
            strategy=AttendancePointsStrategy(),
        )
        PointsService.grant_points(
            user=user,
            activity=attendance,
            strategy=AttendancePointsStrategy(),
        )
        progress = UserProgress.objects.get(user=user)

        self.assertEqual(progress.total_points, 10)

    def test_attendance_transaction_uses_shared_group(self):
        user = self.create_user()
        group = self.create_group()
        attendance = self.create_attendance_record(user, shared_group=group)

        point_transaction = PointsService.grant_points(
            user=user,
            activity=attendance,
            strategy=AttendancePointsStrategy(),
        )

        self.assertEqual(point_transaction.study_group, group)

    def test_invalid_activity_does_not_create_transaction(self):
        user = self.create_user()
        attendance = self.create_attendance_record(user, is_valid=False)

        point_transaction = PointsService.grant_points(
            user=user,
            activity=attendance,
            strategy=AttendancePointsStrategy(),
        )
        progress = UserProgress.objects.get(user=user)

        self.assertIsNone(point_transaction)
        self.assertEqual(PointTransaction.objects.count(), 0)
        self.assertEqual(progress.total_points, 0)
