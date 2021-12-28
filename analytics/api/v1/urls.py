from django.urls import path

from analytics.api.v1.views import SessionAverageView, SessionByWeekView

app_name = 'analytics'

urlpatterns = [
    path('average-duration-binned',
         SessionAverageView.as_view(), name='average-duration'),
    path('session-by-week', SessionByWeekView.as_view(), name='session-by-week'),
]
