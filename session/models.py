import uuid
from django.db import models
from django.contrib.contenttypes.models import ContentType


class Session(models.Model):
    session_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    device_id = models.UUIDField()
    session_name = models.CharField(max_length=255)
    recorded_on = models.DateTimeField(auto_now_add=True)
    duration_in_seconds = models.FloatField()
    is_active = models.BooleanField()

    def __str__(self):
        return f"{self.session_name} [{self.session_id}]"


class Count(models.Model):
    """Table to store count as postgres count is slow for large tables"""
    content_type = models.OneToOneField(
        ContentType,
        related_name="count",
        on_delete=models.CASCADE
    )
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.content_type.name}: {self.count}"
