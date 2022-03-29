from django.db.models import Q
from drf_yasg import openapi
from rest_framework import serializers

from notificationsapp.models import MailoutRecipient, Mailout, MailoutMessage
from settings.commons import TIMEZONES, FILTER_TYPE, SUCCESS_STATUS, \
    FAILURE_STATUS, PENDING_STATUS, RETRY_STATUS, REVOKE_STATUS

PHONE_NUMBER_LEN = 11


def validate_datetime(data):
    start = data.get('datetime_start')
    finish = data.get('datetime_finish')
    if start > finish:
        raise serializers.ValidationError('Finish must occur after start!')
    return data


class RecipientSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=11)
    cell_provider_prefix = serializers.CharField(max_length=3)
    tag = serializers.CharField(max_length=100)
    timezone = serializers.ChoiceField(choices=TIMEZONES)

    class Meta:
        model = MailoutRecipient
        fields = '__all__'

    def validate(self, data):
        phone = data.get('phone')
        prefix = data.get('cell_provider_prefix')
        if not phone.lower().startswith('7') or len(phone) != PHONE_NUMBER_LEN:
            raise serializers.ValidationError(
                'Incorrect phone number provided!')
        if prefix != phone[1:4]:
            raise serializers.ValidationError(
                'Prefix must correspond to the one in the phone number!')
        return data


class RecipientPatchSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=11, required=False)
    cell_provider_prefix = serializers.CharField(max_length=3, required=False)
    tag = serializers.CharField(max_length=100, required=False)
    timezone = serializers.ChoiceField(choices=TIMEZONES, required=False)

    class Meta:
        model = MailoutRecipient
        fields = '__all__'

    def validate(self, data):
        phone = data.get('phone', '')
        prefix = data.get('cell_provider_prefix', '')
        if phone and prefix:
            if not phone.lower().startswith('7') or len(
                    phone) != PHONE_NUMBER_LEN:
                raise serializers.ValidationError(
                    'Incorrect phone number provided!')
            if prefix.lower() != phone[1:4].lower():
                raise serializers.ValidationError(
                    'Prefix must correspond to the one in the phone number!')
        if phone and not prefix:
            if not phone.lower().startswith('7') or len(
                    phone) != PHONE_NUMBER_LEN or phone.lower()[
                                                  1:4] != self.instance.cell_provider_prefix:
                raise serializers.ValidationError(
                    "New phone's prefix doesn't match the prefix on record!")
        if prefix and not phone:
            if prefix.lower() != self.instance.phone[1:4].lower():
                raise serializers.ValidationError(
                    "New prefix doesn't match the prefix of the phone on record!")
        return data


class RecipientDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailoutRecipient


class MailoutSerializer(serializers.ModelSerializer):
    datetime_start = serializers.DateTimeField()
    datetime_finish = serializers.DateTimeField()
    text = serializers.CharField(max_length=2500)
    filter_field = serializers.ChoiceField(choices=FILTER_TYPE)
    filter_value = serializers.CharField(max_length=100)

    class Meta:
        model = Mailout
        fields = ('datetime_start', 'datetime_finish', 'text', 'filter_field',
                  'filter_value',)

    def validate(self, data):
        return validate_datetime(data)


class MailoutPatchSerializer(serializers.ModelSerializer):
    datetime_start = serializers.DateTimeField(required=False)
    datetime_finish = serializers.DateTimeField(required=False)
    text = serializers.CharField(max_length=2500, required=False)
    filter_field = serializers.ChoiceField(choices=FILTER_TYPE, required=False)
    filter_value = serializers.CharField(max_length=100, required=False)

    class Meta:
        model = Mailout
        fields = ('datetime_start', 'datetime_finish', 'text', 'filter_field',
                  'filter_value',)

    def validate(self, data):
        start = data.get('datetime_start', '')
        finish = data.get('datetime_finish', '')
        if start and not finish:
            data['datetime_finish'] = self.instance.datetime_finish
        if finish and not start:
            data['datetime_start'] = self.instance.datetime_start
        return validate_datetime(data)


class MailoutListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailout
        fields = '__all__'
        swagger_schema_fields = {
            "type": openapi.TYPE_OBJECT,
            "properties": {
                "id": openapi.Schema(
                    title="ID",
                    type=openapi.TYPE_NUMBER,
                    read_only=True
                ),
                "datetime_start": openapi.Schema(
                    title="Start date",
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATETIME,
                ),
                "datetime_finish": openapi.Schema(
                    title="Finish date",
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATETIME
                ),
                "text": openapi.Schema(
                    title="Mailout text",
                    type=openapi.TYPE_STRING,
                    max_length=2500
                ),
                "filter_field": openapi.Schema(
                    title="Filter type",
                    type=openapi.TYPE_STRING,
                    enum=["tag", "cell_provider_prefix"]
                ),
                "filter_value": openapi.Schema(
                    title="Filter value",
                    type=openapi.TYPE_STRING,
                    min_length=1,
                    max_length=100
                ),
                "messages": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "sent successfully": openapi.Schema(
                            type=openapi.TYPE_NUMBER
                        ),
                        "sending failed": openapi.Schema(
                            type=openapi.TYPE_NUMBER
                        ),
                        "pending": openapi.Schema(
                            type=openapi.TYPE_NUMBER
                        ),
                        "retried": openapi.Schema(
                            type=openapi.TYPE_NUMBER
                        ),
                        "revoked": openapi.Schema(
                            type=openapi.TYPE_NUMBER
                        ),
                    }
                )
            }
        }

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        successful_messages = MailoutMessage.objects.filter(
            Q(mailout=instance.id) & Q(status=SUCCESS_STATUS)).all().count()
        failed_messages = MailoutMessage.objects.filter(
            Q(mailout=instance.id) & Q(status=FAILURE_STATUS)).all().count()
        pending_messages = MailoutMessage.objects.filter(
            Q(mailout=instance.id) & Q(status=PENDING_STATUS)).all().count()
        retried_messages = MailoutMessage.objects.filter(
            Q(mailout=instance.id) & Q(status=RETRY_STATUS)).all().count()
        revoked_messages = MailoutMessage.objects.filter(
            Q(mailout=instance.id) & Q(status=REVOKE_STATUS)).all().count()
        messages_dict = {
            'sent successfully': successful_messages,
            'sending failed': failed_messages,
            'pending': pending_messages,
            'retried': retried_messages,
            'revoked': revoked_messages
        }
        rep['messages'] = messages_dict
        return rep


class MailoutDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mailout
        fields = '__all__'


class MailoutMessageSerializer(serializers.ModelSerializer):
    recipient = serializers.StringRelatedField()

    class Meta:
        model = MailoutMessage
        fields = ('id', 'sent_at', 'status', 'recipient',)


class MailoutMessagePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailoutMessage
        fields = '__all__'


class MailoutDetailSerializer(serializers.ModelSerializer):
    mailout_message = MailoutMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Mailout
        fields = ('id', 'text', 'datetime_start', 'datetime_finish',
                  'filter_field', 'filter_value', 'mailout_message',)


class MailoutManageSerializer(serializers.ModelSerializer):
    mailout_message = serializers.HyperlinkedRelatedField(
        view_name='message-detail',
        many=True,
        read_only=True
    )

    class Meta:
        model = Mailout
        fields = ('id', 'text', 'datetime_start', 'datetime_finish',
                  'filter_field', 'filter_value', 'mailout_message',)
