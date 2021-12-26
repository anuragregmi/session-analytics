import uuid
import random

from django.db import transaction
from django.core.management.base import BaseCommand
from django.utils import timezone

from session.signals import update_session_count
from session.models import Session


class Command(BaseCommand):
    help = "Seed database with dummy session data"

    def handle(self, *args, **kwargs):
        devices_count = 500
        chunk_size = 1000
        count = 1000000

        device_ids = [uuid.uuid4() for i in range(devices_count)]

        for counter in range(count):
            instances = [
                Session(
                    device_id=random.choice(device_ids),
                    session_name=f"Session {i}",
                    recorded_on=(
                        timezone.now() - timezone.timedelta(
                            minutes=random.randrange(500, 5256000)
                        )
                    ),
                    duration_in_seconds=random.randrange(5, 25000),
                    is_active=random.choice([True, False])
                )
                for i in range(chunk_size)
            ]

            with transaction.atomic:
                Session.objects.bulk_create(instances)
                update_session_count()

            print(f"Created {counter*chunk_size}/{chunk_size*count}", end="\r")
