from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.test import APITestCase

from apps.attendance.models import AttendanceRecord
from apps.groups.models import StudyGroup


User = get_user_model()


class AttendanceRecordModelTests(APITestCase):
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

    def create_record(self, **extra_fields):
        user = extra_fields.pop("user", None) or self.create_user()
        data = {
            "user": user,
            "class_date": date(2026, 6, 14),
            "period": AttendanceRecord.Period.MORNING,
            "photo_url": "https://example.com/photo.jpg",
            **extra_fields,
        }
        return AttendanceRecord.objects.create(**data)

    def test_create_global_attendance_record(self):
        record = self.create_record(shared_group=None)

        self.assertIsNone(record.shared_group)
        self.assertTrue(record.is_valid)
        self.assertEqual(record.points_granted, 10)
        self.assertIsNotNone(record.registered_at)

    def test_create_attendance_record_for_group(self):
        group = self.create_group()
        record = self.create_record(shared_group=group)

        self.assertEqual(record.shared_group, group)

    def test_photo_url_is_required(self):
        record = AttendanceRecord(
            user=self.create_user(),
            class_date=date(2026, 6, 14),
            period=AttendanceRecord.Period.MORNING,
            photo_url="",
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_duplicate_user_date_period_is_blocked(self):
        user = self.create_user()
        self.create_record(user=user)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_record(user=user)

    def test_same_user_same_date_different_period_is_allowed(self):
        user = self.create_user()
        first = self.create_record(user=user, period=AttendanceRecord.Period.MORNING)
        second = self.create_record(
            user=user,
            period=AttendanceRecord.Period.AFTERNOON,
        )

        self.assertNotEqual(first.period, second.period)

    def test_different_users_same_date_same_period_are_allowed(self):
        first = self.create_record(user=self.create_user("ana@example.com"))
        second = self.create_record(user=self.create_user("bia@example.com"))

        self.assertNotEqual(first.user_id, second.user_id)

    def test_points_granted_cannot_be_negative(self):
        record = AttendanceRecord(
            user=self.create_user(),
            class_date=date(2026, 6, 14),
            period=AttendanceRecord.Period.MORNING,
            photo_url="https://example.com/photo.jpg",
            points_granted=-1,
        )

        with self.assertRaises(ValidationError):
            record.full_clean()

    def test_grant_points_returns_points_when_valid(self):
        record = self.create_record(points_granted=15, is_valid=True)

        self.assertEqual(record.grant_points(), 15)

    def test_grant_points_returns_zero_when_invalid(self):
        record = self.create_record(points_granted=15, is_valid=False)

        self.assertEqual(record.grant_points(), 0)

    def test_validate_record_returns_boolean(self):
        valid_record = self.create_record()
        invalid_record = AttendanceRecord(
            user=self.create_user("outro@example.com"),
            class_date=date(2026, 6, 14),
            period=AttendanceRecord.Period.NIGHT,
            photo_url="",
        )

        self.assertTrue(valid_record.validate_record())
        self.assertFalse(invalid_record.validate_record())


class AttendanceRecordApiTests(APITestCase):
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

    def test_list_returns_only_authenticated_user_records(self):
        user_one = self.create_user("ana@example.com")
        user_two = self.create_user("bia@example.com")
        self.client.force_authenticate(user=user_one)
        AttendanceRecord.objects.create(
            user=user_one,
            class_date=date(2026, 6, 14),
            period=AttendanceRecord.Period.MORNING,
            photo_url="https://example.com/a.jpg",
        )
        AttendanceRecord.objects.create(
            user=user_two,
            class_date=date(2026, 6, 14),
            period=AttendanceRecord.Period.AFTERNOON,
            photo_url="https://example.com/b.jpg",
        )

        response = self.client.get("/api/attendance-records/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["period"], AttendanceRecord.Period.MORNING)

    def test_create_binds_record_to_request_user(self):
        user = self.create_user()
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/attendance-records/",
            {
                "class_date": "2026-06-14",
                "period": AttendanceRecord.Period.MORNING,
                "photo_url": "https://example.com/photo.jpg",
                "shared_group": str(self.create_group().id),
                "points_granted": 12,
                "is_valid": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["points_granted"], 10)
        self.assertTrue(response.data["is_valid"])
        record = AttendanceRecord.objects.get(id=response.data["id"])
        self.assertEqual(record.user, user)
        self.assertEqual(record.points_granted, 10)
        self.assertTrue(record.is_valid)
