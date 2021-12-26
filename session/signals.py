from django.db.models import signals
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from session.models import Session, Count


def update_session_count():
    count = Session.objects.all().count()
    content_type = ContentType.objects.get_for_model(Session)

    Count.objects.update_or_create(
        content_type=content_type, defaults={"count": count})


@receiver(signals.post_save, sender=Session)
def post_save_session(sender, created, **kwargs):
    if created:
        update_session_count()


@receiver(signals.post_delete, sender=Session)
def post_delete_session(sender, **kwargs):
    update_session_count()
