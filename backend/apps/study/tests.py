from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APITestCase

from apps.gamification.models import PointTransaction, UserProgress
from apps.study.models import StudySession


User = get_user_model()


class StudySessionModelTests(APITestCase):
    def create_user(self, email="ana@example.com"):
        return User.objects.create_user(
            email=email,
            password="12345678",
            full_name="Ana Silva",
        )

    def create_session(self, **extra_fields):
        user = extra_fields.pop("user", None) or self.create_user()
        data = {
            "user": user,
            "study_date": date(2026, 6, 14),
            "content_description": "Estudo de grafos e Dijkstra",
            "photo_url": "https://example.com/photo.jpg",
            **extra_fields,
        }
        return StudySession.objects.create(**data)

    def test_create_study_session(self):
        session = self.create_session()

        self.assertIsNotNone(session.id)
        self.assertEqual(session.points_granted, 5)
        self.assertTrue(session.is_valid)
        self.assertIsNotNone(session.registered_at)

    def test_photo_url_is_required(self):
        session = StudySession(
            user=self.create_user(),
            study_date=date(2026, 6, 14),
            content_description="Estudo de grafos",
            photo_url="",
        )

        with self.assertRaises(ValidationError):
            session.full_clean()

    def test_content_description_is_required(self):
        session = StudySession(
            user=self.create_user(),
            study_date=date(2026, 6, 14),
            content_description="",
            photo_url="https://example.com/photo.jpg",
        )

        with self.assertRaises(ValidationError):
            session.full_clean()

    def test_points_granted_cannot_be_negative(self):
        session = StudySession(
            user=self.create_user(),
            study_date=date(2026, 6, 14),
            content_description="Estudo de grafos",
            photo_url="https://example.com/photo.jpg",
            points_granted=-1,
        )

        with self.assertRaises(ValidationError):
            session.full_clean()

    def test_grant_points_returns_points_when_valid(self):
        session = self.create_session(points_granted=7, is_valid=True)

        self.assertEqual(session.grant_points(), 7)

    def test_grant_points_returns_zero_when_invalid(self):
        session = self.create_session(points_granted=7, is_valid=False)

        self.assertEqual(session.grant_points(), 0)


class StudySessionApiTests(APITestCase):
    def create_user(self, email="ana@example.com"):
        return User.objects.create_user(
            email=email,
            password="12345678",
            full_name="Ana Silva",
        )

    def test_get_lists_only_authenticated_user_sessions(self):
        user_one = self.create_user("ana@example.com")
        user_two = self.create_user("bia@example.com")
        self.client.force_authenticate(user=user_one)
        StudySession.objects.create(
            user=user_one,
            study_date=date(2026, 6, 14),
            content_description="Estudo A",
            photo_url="https://example.com/a.jpg",
        )
        StudySession.objects.create(
            user=user_two,
            study_date=date(2026, 6, 14),
            content_description="Estudo B",
            photo_url="https://example.com/b.jpg",
        )

        response = self.client.get("/api/study-sessions/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["content_description"], "Estudo A")

    def test_post_creates_session_for_request_user(self):
        user = self.create_user()
        other_user = self.create_user("outra@example.com")
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/study-sessions/",
            {
                "study_date": "2026-06-14",
                "content_description": "Estudo de grafos e Dijkstra",
                "photo_url": "https://example.com/photo.jpg",
                "user": str(other_user.id),
                "is_valid": False,
                "points_granted": 100,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["points_granted"], 5)
        self.assertTrue(response.data["is_valid"])
        session = StudySession.objects.get(id=response.data["id"])
        self.assertEqual(session.user, user)
        self.assertTrue(session.is_valid)
        self.assertEqual(session.points_granted, 5)

    def test_post_generates_point_transaction(self):
        user = self.create_user()
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/study-sessions/",
            {
                "study_date": "2026-06-14",
                "content_description": "Estudo de grafos e Dijkstra",
                "photo_url": "https://example.com/photo.jpg",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        session = StudySession.objects.get(id=response.data["id"])
        transaction = PointTransaction.objects.get(study_session=session)
        self.assertEqual(transaction.user, user)
        self.assertEqual(transaction.points, 5)
        self.assertEqual(
            transaction.source_type,
            PointTransaction.ActivityType.STUDY_SESSION,
        )

    def test_post_updates_user_progress_points_and_streak(self):
        user = self.create_user()
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/study-sessions/",
            {
                "study_date": "2026-06-14",
                "content_description": "Estudo de grafos e Dijkstra",
                "photo_url": "https://example.com/photo.jpg",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        progress = UserProgress.objects.get(user=user)
        self.assertEqual(progress.total_points, 5)
        self.assertEqual(progress.current_streak, 1)
        self.assertEqual(progress.longest_streak, 1)
        self.assertEqual(progress.last_valid_activity_date, date(2026, 6, 14))
