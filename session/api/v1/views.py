from rest_framework import viewsets

from session.models import Session
from session.api.v1.serializers import SessionSerializer


class SessionViewSet(viewsets.ModelViewSet):
    serializer_class = SessionSerializer
    queryset = Session.objects.all()
