import json
from datetime import timedelta

from celery.result import AsyncResult
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_celery_results.models import TaskResult
from rest_framework import status

from notificationsapp.tasks import send_message
from settings.commons import FILTER_TYPE, TIMEZONES, TAG, PHONE_PREFIX, \
    PENDING_STATUS, REVOKE_STATUS, FAILURE_STATUS, SUCCESS_STATUS, RETRY_STATUS


class Mailout(models.Model):
    class Meta:
        verbose_name = 'mailout'
        verbose_name_plural = 'mailouts'
        ordering = ('-datetime_finish',)

    datetime_start = models.DateTimeField(null=False,
                                          verbose_name='start date')
    datetime_finish = models.DateTimeField(null=False,
                                           verbose_name='finish date')
    text = models.TextField(max_length=2500, blank=True,
                            verbose_name='mailout text')
    filter_field = models.CharField(max_length=20, choices=FILTER_TYPE,
                                    verbose_name='filter type')
    filter_value = models.CharField(max_length=100,
                                    verbose_name='filter value')


class MailoutRecipient(models.Model):
    class Meta:
        verbose_name = 'recipient'
        verbose_name_plural = 'recipients'

    phone = models.CharField(max_length=11,
                             verbose_name="recipient's phone")
    cell_provider_prefix = models.CharField(max_length=3,
                                            verbose_name='cell provider prefix')
    tag = models.CharField(max_length=100, verbose_name='recipient tags')
    timezone = models.CharField(max_length=32, choices=TIMEZONES,
                                default='UTC',
                                verbose_name="Recipient's timezone")

    def __str__(self):
        return '%s (tags: %s)' % (self.phone, self.tag)


class MailoutMessage(models.Model):
    class Meta:
        verbose_name = 'message'
        verbose_name_plural = 'messages'
        ordering = ('-sent_at',)

    sent_at = models.DateTimeField(null=True, blank=True,
                                   verbose_name='sent at')
    status = models.CharField(max_length=100, blank=True,
                              verbose_name='message status')
    mailout = models.ForeignKey(Mailout, on_delete=models.CASCADE,
                                related_name='mailout_message',
                                verbose_name='mailout')
    recipient = models.ForeignKey(MailoutRecipient, on_delete=models.CASCADE,
                                  related_name='message_recipient',
                                  verbose_name='message recipient')
    task_id = models.CharField(max_length=100, blank=True, null=True,
                               verbose_name='task ID')

    def apply_async_task(self):
        result = send_message.apply_async(
            args=(self.id, self.recipient.phone, self.mailout.text),
            eta=self.mailout.datetime_start,
            expires=self.mailout.datetime_finish
        )
        self.task_id = result.id
        self.status = PENDING_STATUS
        self.save()


@receiver(post_save, sender=Mailout)
def add_mailout_task(sender, instance, created, **kwargs):
    recipients = []
    if instance.filter_field == TAG:
        recipients = MailoutRecipient.objects.filter(
            tag=instance.filter_value)
    if instance.filter_field == PHONE_PREFIX:
        recipients = MailoutRecipient.objects.filter(
            cell_provider_prefix=instance.filter_value)
    try:
        messages = MailoutMessage.objects.filter(mailout=instance).all()
        if not messages.exists():
            raise MailoutMessage.DoesNotExist
    except MailoutMessage.DoesNotExist:
        for recipient in recipients:
            message = MailoutMessage.objects.create(mailout=instance,
                                                    recipient=recipient)
            message.save()
            message.apply_async_task()
    else:
        for message in messages:
            AsyncResult(message.task_id).revoke()
            if message.status != SUCCESS_STATUS:
                message.delete()
        for recipient in recipients:
            message = MailoutMessage.objects.create(mailout=instance,
                                                    recipient=recipient)
            message.save()
            message.apply_async_task()


@receiver(post_save, sender=TaskResult)
def record_message_status(sender, instance, created, **kwargs):
    delay = timedelta(minutes=10)
    message = MailoutMessage.objects.get(task_id=instance.task_id)
    result_string = json.loads(instance.result)
    result_code = result_string.get('code')
    if result_code == status.HTTP_200_OK:
        message.status = SUCCESS_STATUS
        message.sent_at = instance.date_created
    if result_code == status.HTTP_400_BAD_REQUEST:
        if timezone.now() + delay <= message.mailout.datetime_finish:
            message.status = RETRY_STATUS
            send_message.apply_async(args=(
                message.id, message.recipient.phone, message.mailout.text),
                eta=timezone.now() + delay,
                expires=message.mailout.datetime_finish,
                task_id=instance.task_id
            )
    if instance.status == REVOKE_STATUS:
        message.status = FAILURE_STATUS
    message.save()
