from rest_framework.views import APIView
from rest_framework.response import Response
from analytics.utils import SessionAverageCalculator, SessionByWeekCalculator


class SessionAverageView(APIView):

    def get(self, request) -> Response:
        data = SessionAverageCalculator.get_session_average_data()
        return Response(data)


class SessionByWeekView(APIView):

    def get(self, request) -> Response:
        data = SessionByWeekCalculator.get_session_by_week()
        return Response(data)
