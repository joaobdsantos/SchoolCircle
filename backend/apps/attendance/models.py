import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.groups.models import StudyGroup


class AttendanceRecord(models.Model):
    class Period(models.TextChoices):
        MORNING = "MORNING", "Morning"
        AFTERNOON = "AFTERNOON", "Afternoon"
        NIGHT = "NIGHT", "Night"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendances",
    )
    shared_group = models.ForeignKey(
        StudyGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_records",
    )
    class_date = models.DateField()
    period = models.CharField(max_length=20, choices=Period.choices)
    photo_url = models.ImageField(upload_to="attendance_photos/")
    registered_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)
    points_granted = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "class_date", "period"],
                name="unique_attendance_user_class_date_period",
            ),
            models.CheckConstraint(
                condition=models.Q(points_granted__gte=0),
                name="attendance_points_granted_gte_0",
            ),
        ]

    def clean(self):
        errors = {}

        if not self.photo_url or not str(self.photo_url).strip():
            errors["photo_url"] = "Foto e obrigatoria."

        if self.points_granted is not None and self.points_granted < 0:
            errors["points_granted"] = "Pontos concedidos nao podem ser negativos."

        if errors:
            raise ValidationError(errors)

    def validate_record(self) -> bool:
        try:
            self.full_clean()
        except ValidationError:
            return False
        return True

    def grant_points(self) -> int:
        return self.points_granted if self.is_valid else 0

    def share_to_group(self, group) -> None:
        self.shared_group = group
        self.save(update_fields=["shared_group"])

    def __str__(self):
        return (
            f"AttendanceRecord(user_id={self.user_id}, "
            f"class_date={self.class_date}, period={self.period})"
        )
