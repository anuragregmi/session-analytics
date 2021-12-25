from rest_framework import serializers

from session.models import Session


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ('session_id', 'device_id', 'session_name',
                  'recorded_on', 'duration_in_seconds', 'is_active')
