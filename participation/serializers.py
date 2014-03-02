from rest_framework import serializers
from participation import models
import re


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Participant
        fields = (
            'id', 'first_name', 'last_name', 'birthday', 'phone', 'address',
            'user', 'full_name',
        )
        read_only_fields = ('user',)

    full_name = serializers.Field(source='full_name')

    PHONE_PATTERN = re.compile(r'^(\+?\d+([-\ ]\d+)*)$')

    def validate_phone(self, attrs, field_name):
        if field_name in attrs:
            phone = attrs[field_name]
            if self.PHONE_PATTERN.match(phone) is None:
                raise serializers.ValidationError(
                    'The phone number is not valid')
        return attrs


class OptionItemSerializer(serializers.ModelSerializer):
    currency = serializers.RelatedField(many=False, read_only=False)

    class Meta:
        model = models.OptionItem
        fields = ('id', 'name', 'key', 'price', 'currency')


class OptionListSerializer(serializers.ModelSerializer):
    option_item = OptionItemSerializer(many=False, read_only=True)

    class Meta:
        model = models.Option
        fields = ('option_item',)


class OptionCreateSerializer(serializers.ModelSerializer):
    option_item = serializers.RelatedField(many=False, read_only=False)

    class Meta:
        model = models.Option
        fields = ('option_item',)


class ParticipationSerializer(serializers.ModelSerializer):
    options = OptionListSerializer(many=True, read_only=True)

    class Meta:
        model = models.Participation
        fields = ('participant', 'conference', 'options', 'status')
        read_only_fields = ('status',)
