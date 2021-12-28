import pandas as pd

from django.db import connection
from django.db.models import Max, Avg, Q, QuerySet, F, Value, CharField, Count
from django.db.models.functions import Concat, Floor, ExtractWeek, ExtractYear, ExtractMonth, Round
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from session.models import Session


class SessionAverageView(APIView):

    def get_queryset(self) -> QuerySet:
        return Session.objects.all()

    def get_bins(self, queryset, return_pair=False) -> list:
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
        # 3.26 sec REQUEST-RESPONSE
        cursor = connection.cursor()

        # did the same thing
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
        return map(lambda item: {'bin': item[0], "avg": round(item[1], 2)}, cursor.fetchall())

    def get(self, request) -> Response:
        # data = self._bin_using_pandas(self.get_queryset())
        # data = self._bin_using_orm_using_aggregate(self.get_queryset())
        # data = self._bin_using_orm_using_group_by(self.get_queryset())
        data = self._bin_using_raw_sql()
        return Response(data)


class SessionByWeekView(APIView):
    def get_queryset(self):
        return Session.objects.all()

    def get(self, request):
        qs = self.get_queryset()

        # to limit cache size we limit records to last 5 years
        qs = qs.filter(recorded_on__date__year__gte=timezone.now().year-5)

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

        return Response(qs)
