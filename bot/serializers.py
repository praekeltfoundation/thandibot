from django.http import Http404

from .models import Record, BotSubscriptionRelation
from rest_framework import serializers


class RecordSerializer(serializers.Serializer):
    message_uuid = serializers.CharField()
    status = serializers.CharField()
    to_addr = serializers.CharField()
    timestamp = serializers.DateTimeField(allow_null=True)
    channel = serializers.CharField(default=BotSubscriptionRelation.WHATSAPP)


class EventSerializer(serializers.Serializer):
    data = RecordSerializer()

    def create(self, validated_data):
        data = validated_data['data']

        bot_msisdn = data['to_addr']
        rel = BotSubscriptionRelation.objects.filter(
            urn=bot_msisdn, channel=data['channel']).first()

        if not rel:
            raise Http404

        if data['status'] == 'delivered':
            record, _ = Record.objects.get_or_create(
                bot_subcription_relation=rel,
                message=data['message_uuid'],
                received_at=data['timestamp'])

        return validated_data
