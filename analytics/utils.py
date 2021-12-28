import pandas as pd

from django.core.cache import cache
from django.db import connection
from django.db.models import Max, Avg, Q, QuerySet, F, Value, CharField, Count
from django.db.models.functions import Concat, Floor, ExtractWeek, ExtractYear, ExtractMonth, Round
from django.utils import timezone

from session.models import Session


class SessionAverageCalculator:

    CACHE_KEY = 'session_average_data'

    @classmethod
    def get_bins(cls, queryset, return_pair=False) -> list:
        """Get bins for given queryset

        Returns:
            IF return_pair is False(default):
                flat list of integers will be returned
            ELSE
                list containing pair of left and right edges of 
                bin will be returned
        """
        max_duration = str(int(queryset.aggregate(
            max=Max('duration_in_seconds')
        ).get('max')))

        start = int(f"{max_duration[:-1]}0")
        end = start + 10

        bins = [
            (counter, counter+10) if return_pair else counter
            for counter in range(0, end+10, 10)
        ]

        return bins

    @classmethod
    def _bin_using_orm_using_aggregate(cls, queryset: QuerySet) -> dict:
        #  13.31 s REQUEST - RESPONSE
        bins = cls.get_bins(queryset, return_pair=True)

        agg = queryset.aggregate(
            **{
                f"{_start}-{_end}": Avg(
                    'duration_in_seconds',
                    filter=Q(
                        duration_in_seconds__range=[_start, _end]
                    )
                )
                for (_start, _end) in bins
            }
        )

        return map(lambda item: {'bin': item[0], 'avg': round(item[1] or 0, 2)}, agg.items())

    @classmethod
    def _bin_using_orm_using_group_by(cls, queryset: QuerySet) -> dict:
        #  8.96s REQUEST - RESPONSE

        qs = queryset.annotate(
            # (F('duration_in_seconds') - 1) to include 10 in 0-10 bin
            # Floor(Value/10) * 10 to convert last digit to 0
            bin_start=Floor((F('duration_in_seconds') - 1) / 10) * 10
        )

        # GroupBy bin_start and then calculate average
        qs = qs.order_by('bin_start').values(
            'bin_start',
        ).annotate(
            avg=Round(Avg('duration_in_seconds'), 2),
            bin=Concat(
                'bin_start', Value('-'), F('bin_start') + 10,
                output_field=CharField()
            )
        ).values('avg', 'bin')

        return qs

    @classmethod
    def _bin_using_pandas(cls, queryset: QuerySet) -> dict:
        #  54.42 s

        df = pd.DataFrame(queryset.values('duration_in_seconds'))
        avg = df.groupby(
            pd.cut(df['duration_in_seconds'],
                   cls.get_bins(queryset), right=True)
        ).mean()

        return [
            {
                'bin': f"{index.left}-{index.right}",
                'avg': round(avg['duration_in_seconds'][index], 2)
            }
            for index in avg.index
        ]

    @classmethod
    def _bin_using_raw_sql(cls) -> dict:
        # 3.26s
        cursor = connection.cursor()

        # did the same thing as groupby in django ORM
        query = '''
        SELECT CONCAT(t.start, '-', t.start + 10), t.avg
        FROM
        (
            SELECT
                AVG("session_session"."duration_in_seconds") AS "avg",
                (FLOOR(("session_session"."duration_in_seconds" - 1) / 10) * 10) as "start"
            FROM session_session
            GROUP BY "start"
            ORDER BY "start"
        ) t
        '''

        cursor.execute(query)
        return list(
            map(lambda item: {'bin': item[0], "avg": round(
                item[1], 2)}, cursor.fetchall())
        )

    @classmethod
    def calculate_session_average_data(cls) -> list:
        """Calculates average data

        Data is calculated using raw sql as it was found to be most efficient
        """

        return cls._bin_using_raw_sql()

    @classmethod
    def set_or_update_cache(cls) -> list:
        """Updates cache"""
        data = cls.calculate_session_average_data()
        cache.set(
            cls.CACHE_KEY,
            data
        )
        return data

    @classmethod
    def get_session_average_data(cls) -> list:
        """Get session average data from cache if set otherwise set"""

        data = cache.get(cls.CACHE_KEY)
        if not data:
            data = cls.set_or_update_cache()

        return data


class SessionByWeekCalculator:
    CACHE_KEY = 'session_by_week'

    @classmethod
    def calculate_session_by_week(cls) -> list:
        qs = Session.objects.filter(
            recorded_on__date__year__gte=timezone.now().year-5)

        qs = qs.annotate(
            year=ExtractYear('recorded_on'),
            month=ExtractMonth('recorded_on'),
            week=ExtractWeek('recorded_on')
        ).order_by('year', 'week').values(
            'year', 'month', 'week'
        ).annotate(
            count=Count('session_id'),
            active_count=Count('session_id', filter=Q(is_active=True))
        )

        return list(qs)

    @classmethod
    def set_or_update_cache(cls) -> list:
        data = cls.calculate_session_by_week()
        cache.set(
            cls.CACHE_KEY,
            data
        )
        return data

    @classmethod
    def get_session_by_week(cls) -> list:
        """Get session average data from cache if set otherwise set"""

        data = cache.get(cls.CACHE_KEY)
        if not data:
            data = cls.set_or_update_cache()

        return data
