from datetime import date

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.attendance.models import AttendanceRecord
from apps.gamification.models import PointTransaction
from apps.gamification.strategies import (
    AttendancePointsStrategy,
    StudySessionPointsStrategy,
)
from apps.study.models import StudySession


User = get_user_model()


class PointsStrategyTests(APITestCase):
    def create_user(self, email="ana@example.com"):
        return User.objects.create_user(
            email=email,
            password="12345678",
            full_name="Ana Silva",
        )

    def test_attendance_strategy_calculates_points(self):
        attendance = AttendanceRecord(
            user=self.create_user(),
            class_date=date(2026, 6, 14),
            period=AttendanceRecord.Period.MORNING,
            photo_url="https://example.com/photo.jpg",
            points_granted=10,
        )
        strategy = AttendancePointsStrategy()

        self.assertEqual(strategy.calculate(attendance), 10)

    def test_attendance_strategy_returns_source_type(self):
        strategy = AttendancePointsStrategy()

        self.assertEqual(
            strategy.get_source_type(),
            PointTransaction.ActivityType.ATTENDANCE,
        )

    def test_attendance_strategy_returns_activity_date(self):
        attendance = AttendanceRecord(
            user=self.create_user(),
            class_date=date(2026, 6, 14),
            period=AttendanceRecord.Period.MORNING,
            photo_url="https://example.com/photo.jpg",
        )
        strategy = AttendancePointsStrategy()

        self.assertEqual(strategy.get_activity_date(attendance), attendance.class_date)

    def test_attendance_strategy_returns_reason(self):
        strategy = AttendancePointsStrategy()

        self.assertTrue(strategy.get_reason(object()))

    def test_attendance_strategy_returns_zero_for_invalid_activity(self):
        attendance = AttendanceRecord(
            user=self.create_user(),
            class_date=date(2026, 6, 14),
            period=AttendanceRecord.Period.MORNING,
            photo_url="https://example.com/photo.jpg",
            is_valid=False,
            points_granted=10,
        )
        strategy = AttendancePointsStrategy()

        self.assertEqual(strategy.calculate(attendance), 0)

    def test_study_session_strategy_calculates_points(self):
        session = StudySession(
            user=self.create_user(),
            study_date=date(2026, 6, 14),
            content_description="Estudo de grafos e Dijkstra",
            photo_url="https://example.com/photo.jpg",
            points_granted=5,
        )
        strategy = StudySessionPointsStrategy()

        self.assertEqual(strategy.calculate(session), 5)

    def test_study_session_strategy_returns_source_type(self):
        strategy = StudySessionPointsStrategy()

        self.assertEqual(
            strategy.get_source_type(),
            PointTransaction.ActivityType.STUDY_SESSION,
        )

    def test_study_session_strategy_returns_activity_date(self):
        session = StudySession(
            user=self.create_user(),
            study_date=date(2026, 6, 14),
            content_description="Estudo de grafos e Dijkstra",
            photo_url="https://example.com/photo.jpg",
        )
        strategy = StudySessionPointsStrategy()

        self.assertEqual(strategy.get_activity_date(session), session.study_date)

    def test_study_session_strategy_returns_reason(self):
        strategy = StudySessionPointsStrategy()

        self.assertTrue(strategy.get_reason(object()))

    def test_study_session_strategy_returns_zero_for_invalid_activity(self):
        session = StudySession(
            user=self.create_user(),
            study_date=date(2026, 6, 14),
            content_description="Estudo de grafos e Dijkstra",
            photo_url="https://example.com/photo.jpg",
            is_valid=False,
            points_granted=5,
        )
        strategy = StudySessionPointsStrategy()

        self.assertEqual(strategy.calculate(session), 0)
