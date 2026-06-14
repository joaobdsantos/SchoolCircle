import uuid

from django.db import models


class StudyGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_group(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self.save(update_fields=["name", "description", "updated_at"])

    def __str__(self):
        return self.name
