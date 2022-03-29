from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView, \
    DestroyAPIView, ListAPIView, RetrieveAPIView
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin, \
    DestroyModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet

from notificationsapp.models import MailoutRecipient, Mailout, MailoutMessage
from notificationsapp.serializers import RecipientSerializer, \
    RecipientPatchSerializer, RecipientDeleteSerializer, MailoutSerializer, \
    MailoutListSerializer, MailoutDeleteSerializer, MailoutDetailSerializer, \
    MailoutMessageSerializer, MailoutMessagePostSerializer, \
    MailoutManageSerializer, MailoutPatchSerializer


class RecipientPostApiView(CreateAPIView):
    serializer_class = RecipientSerializer
    queryset = MailoutRecipient.objects.all()

    @swagger_auto_schema(
        operation_id='recipient_create',
        request_body=RecipientSerializer,
        operation_description='POST-request to create an instance of Recipient',
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Bad request, check the params'
            )
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RecipientPutApiView(GenericAPIView, UpdateModelMixin):
    serializer_class = RecipientPatchSerializer
    queryset = MailoutRecipient.objects.all()

    @swagger_auto_schema(
        operation_id='recipient_update',
        request_body=RecipientPatchSerializer,
        operation_description='Partial update of Recipient object',
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Bad request',
                examples={
                    "application/json": {
                        "non_field_errors": [
                            "New phone's prefix doesn't match the prefix on record!"
                        ]
                    }
                }
            )
        }
    )
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RecipientDeleteApiView(DestroyAPIView):
    serializer_class = RecipientDeleteSerializer
    queryset = MailoutRecipient.objects.all()

    @swagger_auto_schema(
        operation_id='recipient_delete',
        request_body=no_body,
        operation_description='Delete an instance of Recipient',
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="No instance with that ID exists"
            ),
            status.HTTP_200_OK: openapi.Response(
                description="Deleted successfully"
            )
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class MailoutCreateApiView(CreateAPIView):
    serializer_class = MailoutSerializer
    queryset = Mailout.objects.all()

    @swagger_auto_schema(
        operation_id='mailout_create',
        request_body=MailoutSerializer,
        operation_description='POST-request to create an instance of Mailout',
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Bad request, check the params'
            )
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MailoutListApiView(ListAPIView):
    serializer_class = MailoutListSerializer
    queryset = Mailout.objects.all()

    @swagger_auto_schema(
        operation_id='mailout_list',
        request_body=no_body,
        operation_description='Receive the paginated list of all existing mailouts'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MailoutDeleteApiView(DestroyAPIView):
    serializer_class = MailoutDeleteSerializer
    queryset = Mailout.objects.all()

    @swagger_auto_schema(
        operation_id='mailout_delete',
        request_body=no_body,
        operation_description='Delete an instance of Mailout',
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="No instance with that ID exists"
            ),
            status.HTTP_200_OK: openapi.Response(
                description="Deleted successfully"
            )
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class MailoutPatchApiView(GenericAPIView, UpdateModelMixin):
    queryset = Mailout.objects.all()
    serializer_class = MailoutPatchSerializer

    @swagger_auto_schema(
        operation_id='mailout_update',
        request_body=MailoutPatchSerializer,
        operation_description='Partial update of Mailout object',
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Bad request',
                examples={
                    "application/json": {
                        "non_field_errors": [
                            "Finish must occur after start!"
                        ]
                    }
                }
            )
        }
    )
    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class MailoutDetailApiView(RetrieveAPIView):
    serializer_class = MailoutDetailSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Mailout.objects.filter(pk=pk)

    @swagger_auto_schema(
        operation_id='mailout_read',
        request_body=no_body,
        operation_description='Detailed information for a single Mailout object instance',
        responses={
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description='Bad request',
                examples={
                    "application/json": {
                        "detail": [
                            "Not found."
                        ]
                    }
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MailoutManageViewSet(GenericViewSet,
                           RetrieveModelMixin,
                           UpdateModelMixin,
                           DestroyModelMixin,
                           ListModelMixin):

    def get_queryset(self):
        return Mailout.objects.filter(datetime_finish__gte=timezone.now())

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return MailoutPatchSerializer
        else:
            return MailoutManageSerializer

    @swagger_auto_schema(
        operation_id='manage_mailout_list',
        request_body=no_body,
        operation_description='Receive the paginated list of all active mailouts (datetime_finish < current time)'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='manage_mailout_read',
        request_body=no_body,
        operation_description='Receive the info about a single instance of active mailouts (datetime_finish < current time)',
        responses={
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description='Bad request',
                examples={
                    "application/json": {
                        "detail": [
                            "Not found."
                        ]
                    }
                }
            )
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='manage_mailout_update',
        request_body=MailoutManageSerializer,
        operation_description='Update of a single instance of active Mailout objects (datetime_finish < current time)',
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Bad request',
                examples={
                    "application/json": {
                        "non_field_errors": [
                            "Finish must occur after start!"
                        ]
                    }
                }
            )
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='manage_mailout_partial_update',
        request_body=MailoutPatchSerializer,
        operation_description='Partial update of a single instance of active Mailout objects (datetime_finish < current time)',
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Bad request',
                examples={
                    "application/json": {
                        "non_field_errors": [
                            "Finish must occur after start!"
                        ]
                    }
                }
            )
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='manage_mailout_delete',
        request_body=no_body,
        operation_description='Delete an instance of active Mailout (datetime_finish < current time)',
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="No instance with that ID exists"
            ),
            status.HTTP_200_OK: openapi.Response(
                description="Deleted successfully"
            )
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class MailoutMessageDetailApiView(GenericViewSet,
                                  RetrieveModelMixin,
                                  UpdateModelMixin,
                                  DestroyModelMixin,
                                  ListModelMixin):

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return MailoutMessage.objects.filter(pk=pk).filter(
            mailout__datetime_finish__gte=timezone.now())

    def get_serializer_class(self):
        if self.request.method in ['GET', 'DELETE']:
            return MailoutMessageSerializer
        return MailoutMessagePostSerializer

    @swagger_auto_schema(
        operation_id='manage_message_list',
        request_body=no_body,
        operation_description='Receive the paginated list of all messages in active mailouts (datetime_finish < current time)'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='manage_message_read',
        request_body=no_body,
        operation_description='Receive the info about a single instance of messages in active mailouts (datetime_finish < current time)',
        responses={
            status.HTTP_404_NOT_FOUND: openapi.Response(
                description='Bad request',
                examples={
                    "application/json": {
                        "detail": [
                            "Not found."
                        ]
                    }
                }
            )
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='manage_message_update',
        request_body=MailoutMessagePostSerializer,
        operation_description='Update of a single instance of Message in an active Mailout (datetime_finish < current time)',
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Bad request',
                examples={
                    "application/json": {
                        "non_field_errors": [
                            "Finish must occur after start!"
                        ]
                    }
                }
            )
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='manage_message_partial_update',
        request_body=MailoutMessagePostSerializer,
        operation_description='Partial update of a single instance of Message in an active Mailout (datetime_finish < current time)',
        responses={
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description='Bad request',
                examples={
                    "application/json": {
                        "non_field_errors": [
                            "Finish must occur after start!"
                        ]
                    }
                }
            )
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='manage_message_delete',
        request_body=no_body,
        operation_description='Delete an instance of Message in active Mailout (datetime_finish < current time)',
        responses={
            status.HTTP_204_NO_CONTENT: openapi.Response(
                description="No instance with that ID exists"
            ),
            status.HTTP_200_OK: openapi.Response(
                description="Deleted successfully"
            )
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
