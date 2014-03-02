from rest_framework import serializers

from .models import Prelection


class PrelectionSerializer(serializers.ModelSerializer):
    """Basic prelection serializer. .status can only be changed by redactors,
    and it's done together with changing time"""
    class Meta:
        model = Prelection
        read_only_fields = ('status', 'time')
