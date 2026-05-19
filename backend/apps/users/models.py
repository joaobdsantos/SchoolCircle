from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    pass


class AcademicProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="academic_profile",
    )
    education_level = models.CharField(max_length=100)
    is_independent = models.BooleanField(default=False)
    institution_name = models.CharField(max_length=255, blank=True)
    course_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AcademicProfile(user_id={self.user_id})"
