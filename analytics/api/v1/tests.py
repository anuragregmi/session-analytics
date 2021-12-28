from django.core.cache import cache
from django.urls import reverse

from rest_framework.test import APITestCase

from analytics.utils import SessionAverageCalculator, SessionByWeekCalculator


class AnalyticsTestCase(APITestCase):

    def test_session_average_duration(self):
        data_in_cache = [
            {
                'bin': '0-10',
                'avg': 5.5
            },
            {
                'bin': '10-20',
                'avg': 9.1
            }
        ]
        cache.set(SessionAverageCalculator.CACHE_KEY, data_in_cache)
        url = reverse('analytics:average-duration')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), data_in_cache)

    def test_session_average_duration(self):
        data_in_cache = [
            {
                'year': 2021,
                'month': 1,
                'week': 1,
                'count': 2,
                'active_count': 2
            },
            {
                'year': 2021,
                'month': 1,
                'week': 2,
                'count': 2,
                'active_count': 1
            },
        ]
        cache.set(SessionByWeekCalculator.CACHE_KEY, data_in_cache)
        url = reverse('analytics:session-by-week')

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), data_in_cache)

    def tearDown(self):
        cache.delete(SessionAverageCalculator.CACHE_KEY)
        cache.delete(SessionByWeekCalculator.CACHE_KEY)
