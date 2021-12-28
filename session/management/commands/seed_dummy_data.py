import uuid
import random

from django.db import transaction
from django.core.management.base import BaseCommand
from django.utils import timezone

from session.signals import update_session_count
from session.models import Session


class Command(BaseCommand):
    help = "Seed database with dummy session data for testing"

    def handle(self, *args, **kwargs):

        devices_count = 500
        chunk_size = 10000
        count = 1000

        delete_qs = Session.objects.all()
        delete_qs._raw_delete(delete_qs.db)

        device_ids = [uuid.uuid4() for i in range(devices_count)]

        try:

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
                        duration_in_seconds=random.randrange(5, 1000),
                        is_active=random.choice([True, False])
                    )
                    for i in range(chunk_size)
                ]

                Session.objects.bulk_create(instances, batch_size=chunk_size)
                print(
                    f"Created {(counter+1)*chunk_size}/{chunk_size*count}", end="\r")
        finally:
            update_session_count()
