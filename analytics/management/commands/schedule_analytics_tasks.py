from django.core.management.base import BaseCommand

from django_q.models import Schedule


class Command(BaseCommand):
    help = "Schedule tasks: update cache in every 5 minutes"

    def handle(self, *args, **kwargs):
        Schedule.objects.create(
            func='analytics.utils.SessionAverageCalculator.set_or_update_cache',
            schedule_type=Schedule.MINUTES,
            minutes=5
        )
        Schedule.objects.create(
            func='analytics.utils.SessionByWeekCalculator.set_or_update_cache',
            schedule_type=Schedule.MINUTES,
            minutes=5
        )
