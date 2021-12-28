import uuid
import datetime

from collections import defaultdict

from django.test import TestCase
from django.utils import timezone

from analytics.utils import SessionAverageCalculator, SessionByWeekCalculator
from session.models import Session


class TestSessionAverageCalculator(TestCase):

    def setUp(self):

        # (0-10)
        Session.objects.create(
            device_id=uuid.uuid4(),
            session_name=f"Session 1",
            recorded_on=timezone.now(),
            duration_in_seconds=3,
            is_active=True
        )
        Session.objects.create(
            device_id=uuid.uuid4(),
            session_name=f"Session 2",
            recorded_on=timezone.now(),
            duration_in_seconds=10,
            is_active=True
        )

        # 10 - 20
        Session.objects.create(
            device_id=uuid.uuid4(),
            session_name=f"Session 3",
            recorded_on=timezone.now(),
            duration_in_seconds=11,
            is_active=True
        )
        Session.objects.create(
            device_id=uuid.uuid4(),
            session_name=f"Session 4",
            recorded_on=timezone.now(),
            duration_in_seconds=12.5,
            is_active=True
        )

        Session.objects.create(
            device_id=uuid.uuid4(),
            session_name=f"Session 5",
            recorded_on=timezone.now(),
            duration_in_seconds=19,
            is_active=True
        )

    def test_calculator(self):
        data = SessionAverageCalculator.calculate_session_average_data()

        expected_data = [
            {
                'bin': '0-10',
                'avg': round((10+3)/2, 2)
            },
            {
                'bin': '10-20',
                'avg': round((11+12.5+19)/3, 2)
            }
        ]

        self.assertEqual(expected_data, data)


class TestSessionByWeekCalculator(TestCase):
    def setUp(self):
        year = timezone.now().year - 1

        self.active_dates = [
            datetime.date(year, 1, 1),
            datetime.date(year, 1, 5),
            datetime.date(year, 1, 10),
            datetime.date(year, 1, 13),
            datetime.date(year, 2, 6),
            datetime.date(year, 2, 27),
            datetime.date(year, 3, 19),
            datetime.date(year, 4, 11),
            datetime.date(year, 4, 12),
            datetime.date(year, 5, 29),
        ]

        self.inactive_dates = [
            datetime.date(year, 1, 11),
            datetime.date(year, 1, 14),
            datetime.date(year, 1, 15),
            datetime.date(year, 2, 11),
            datetime.date(year, 2, 20),
            datetime.date(year, 3, 6),
            datetime.date(year, 3, 10),
            datetime.date(year, 4, 1),
            datetime.date(year, 4, 17),
            datetime.date(year, 5, 26),
        ]

        for date_ in self.active_dates:

            Session.objects.create(
                device_id=uuid.uuid4(),
                session_name=f"Session 1",
                recorded_on=timezone.datetime.combine(
                    date_, timezone.now().timetz()
                ),
                duration_in_seconds=3,
                is_active=True
            )

        for date_ in self.inactive_dates:

            Session.objects.create(
                device_id=uuid.uuid4(),
                session_name=f"Session 1",
                recorded_on=timezone.datetime.combine(
                    date_, timezone.now().timetz()
                ),
                duration_in_seconds=3,
                is_active=False
            )

    def test_session_by_week_calculator(self):
        week_count = defaultdict(lambda: dict(**{
            'count': 0, 'active': 0
        }))

        for date in self.active_dates:
            week_number = date.isocalendar()[1]
            key = f"{week_number}-{date.month}"

            week_count[key] = {
                'count': week_count[key]['count'] + 1,
                'active': week_count[key]['active'] + 1
            }

        for date in self.inactive_dates:
            week_number = date.isocalendar()[1]
            key = f"{week_number}-{date.month}"

            week_count[key] = {
                'count': week_count[key]['count'] + 1,
                'active': week_count[key]['active']
            }

        result = SessionByWeekCalculator.calculate_session_by_week()

        for week_number_month, counts in week_count.items():
            week_number, month = week_number_month.split("-")

            week_data_from_result = next(filter(
                lambda item: item["week"] == int(
                    week_number) and item["month"] == int(month),
                result
            ))

            self.assertEqual(
                week_data_from_result["count"], counts["count"]
            )
            self.assertEqual(
                week_data_from_result["active_count"], counts["active"]
            )
