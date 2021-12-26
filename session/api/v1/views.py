from django.db import transaction
from rest_framework import viewsets


from session.models import Session
from session.pagination import SessionPagination
from session.api.v1.serializers import SessionSerializer


class SessionViewSet(viewsets.ModelViewSet):
    serializer_class = SessionSerializer
    queryset = Session.objects.all()
    pagination_class = SessionPagination

    # we need to perform save and post save operations in atomic block
    @transaction.atomic
    def perform_create(self, serializer):
        return super().perform_create(serializer)

    @transaction.atomic
    def perform_destroy(self, instance):
        return super().perform_destroy(instance)
