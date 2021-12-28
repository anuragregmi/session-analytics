from django.urls import path

from analytics.api.v1.views import SessionAverageView, SessionByWeekView

urlpatterns = [
    path('average-duration-binned', SessionAverageView.as_view()),
    path('session-by-week', SessionByWeekView.as_view()),
]
