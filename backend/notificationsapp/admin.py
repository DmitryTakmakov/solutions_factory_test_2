from django.contrib import admin

from notificationsapp.models import Mailout, MailoutRecipient, MailoutMessage

admin.site.register((Mailout, MailoutRecipient, MailoutMessage,))
