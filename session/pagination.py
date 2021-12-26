from collections import OrderedDict

from django.core.paginator import Paginator as DJPaginator
from django.utils.functional import cached_property
from django.contrib.contenttypes.models import ContentType

from rest_framework.pagination import PageNumberPagination as DRFPageNumberPagination
from rest_framework.response import Response

from session.models import Count, Session


class SessionPaginator(DJPaginator):
    @cached_property
    def count(self):
        ct = ContentType.objects.get_for_model(Session)
        return getattr(Count.objects.filter(content_type=ct).first(), 'count', 0)


class SessionPagination(DRFPageNumberPagination):
    django_paginator_class = SessionPaginator
