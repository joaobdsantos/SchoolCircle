from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.test import APITestCase

from apps.gamification.models import UserProgress

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
