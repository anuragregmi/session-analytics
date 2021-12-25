import uuid
from django.db import models


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
