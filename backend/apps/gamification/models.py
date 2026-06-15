import uuid
from datetime import date, timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class UserProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="progress",
    )
    current_streak = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
    )
    longest_streak = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
    )
    total_points = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
    )
    last_valid_activity_date = models.DateField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(current_streak__gte=0),
                name="user_progress_current_streak_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(longest_streak__gte=0),
                name="user_progress_longest_streak_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(total_points__gte=0),
                name="user_progress_total_points_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(longest_streak__gte=models.F("current_streak")),
                name="user_progress_longest_gte_current",
            ),
        ]

    def clean(self):
        errors = {}

        if self.total_points is not None and self.total_points < 0:
            errors["total_points"] = "Total de pontos nao pode ser negativo."

        if self.current_streak is not None and self.current_streak < 0:
            errors["current_streak"] = "Sequencia atual nao pode ser negativa."

        if self.longest_streak is not None and self.longest_streak < 0:
            errors["longest_streak"] = "Maior sequencia nao pode ser negativa."

        if (
            self.current_streak is not None
            and self.longest_streak is not None
            and self.longest_streak < self.current_streak
        ):
            errors["longest_streak"] = (
                "Maior sequencia deve ser maior ou igual a atual."
            )

        if errors:
            raise ValidationError(errors)

    def add_points(self, points: int) -> None:
        if points < 0:
            raise ValidationError("Pontos nao podem ser negativos.")

        self.total_points += points
        self.save(update_fields=["total_points"])

    def update_streak(self, activity_date: date) -> None:
        if self.last_valid_activity_date == activity_date:
            return

        if (
            self.last_valid_activity_date is not None
            and activity_date < self.last_valid_activity_date
        ):
            return

        if (
            self.last_valid_activity_date is not None
            and activity_date == self.last_valid_activity_date + timedelta(days=1)
        ):
            self.current_streak += 1
        else:
            self.current_streak = 1

        self.longest_streak = max(self.longest_streak, self.current_streak)
        self.last_valid_activity_date = activity_date
        self.save(
            update_fields=[
                "current_streak",
                "longest_streak",
                "last_valid_activity_date",
            ]
        )

    def reset_streak(self) -> None:
        self.current_streak = 0
        self.save(update_fields=["current_streak"])

    def __str__(self):
        return f"UserProgress(user_id={self.user_id}, total_points={self.total_points})"


class PointTransaction(models.Model):
    class ActivityType(models.TextChoices):
        ATTENDANCE = "ATTENDANCE", "Attendance"
        STUDY_SESSION = "STUDY_SESSION", "Study session"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="point_transactions",
    )
    points = models.IntegerField()
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    source_type = models.CharField(
        max_length=20,
        choices=ActivityType.choices,
    )
    attendance_record = models.ForeignKey(
        "attendance.AttendanceRecord",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="point_transactions_from_attendance",
    )
    study_session = models.ForeignKey(
        "study.StudySession",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="point_transactions_from_study_session",
    )
    study_group = models.ForeignKey(
        "groups.StudyGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="point_transactions_from_group",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(points=0),
                name="point_transaction_points_not_zero",
            ),
        ]

    def clean(self):
        errors = {}

        if self.points == 0:
            errors["points"] = "Pontos nao podem ser zero."

        if not self.reason or not str(self.reason).strip():
            errors["reason"] = "Motivo e obrigatorio."

        if self.attendance_record_id and self.study_session_id:
            errors["study_session"] = (
                "AttendanceRecord e StudySession nao podem ser usados ao mesmo tempo."
            )

        if self.source_type == self.ActivityType.ATTENDANCE:
            if not self.attendance_record_id:
                errors["attendance_record"] = (
                    "AttendanceRecord e obrigatorio para transacao de attendance."
                )
            if self.study_session_id:
                errors["study_session"] = (
                    "StudySession deve ficar vazio para transacao de attendance."
                )

        if self.source_type == self.ActivityType.STUDY_SESSION:
            if not self.study_session_id:
                errors["study_session"] = (
                    "StudySession e obrigatorio para transacao de estudo."
                )
            if self.attendance_record_id:
                errors["attendance_record"] = (
                    "AttendanceRecord deve ficar vazio para transacao de estudo."
                )

        if (
            self.attendance_record_id
            and self.user_id
            and self.attendance_record.user_id != self.user_id
        ):
            errors["attendance_record"] = (
                "AttendanceRecord deve pertencer ao mesmo usuario da transacao."
            )

        if (
            self.study_session_id
            and self.user_id
            and self.study_session.user_id != self.user_id
        ):
            errors["study_session"] = (
                "StudySession deve pertencer ao mesmo usuario da transacao."
            )

        if errors:
            raise ValidationError(errors)

    def is_from_attendance(self) -> bool:
        return self.source_type == self.ActivityType.ATTENDANCE

    def is_from_study_session(self) -> bool:
        return self.source_type == self.ActivityType.STUDY_SESSION

    def is_group_scoped(self) -> bool:
        return self.study_group_id is not None

    def __str__(self):
        return (
            f"PointTransaction(user_id={self.user_id}, points={self.points}, "
            f"source_type={self.source_type})"
        )
