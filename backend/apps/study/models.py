import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class StudySession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="study_sessions",
    )
    study_date = models.DateField()
    content_description = models.TextField()
    photo_url = models.URLField(max_length=500)
    registered_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)
    points_granted = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(points_granted__gte=0),
                name="study_session_points_granted_gte_0",
            ),
        ]

    def clean(self):
        errors = {}

        if not self.content_description or not str(self.content_description).strip():
            errors["content_description"] = "Descricao do estudo e obrigatoria."

        if not self.photo_url or not str(self.photo_url).strip():
            errors["photo_url"] = "Photo URL e obrigatoria."

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

    def __str__(self):
        return f"StudySession(user_id={self.user_id}, study_date={self.study_date})"
