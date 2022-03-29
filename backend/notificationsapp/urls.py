from django.urls import path, include
from rest_framework import routers

from notificationsapp.views import RecipientPostApiView, RecipientPutApiView, \
    RecipientDeleteApiView, MailoutCreateApiView, MailoutListApiView, \
    MailoutDeleteApiView, MailoutPatchApiView, MailoutDetailApiView, \
    MailoutManageViewSet, MailoutMessageDetailApiView

router = routers.DefaultRouter()
router.register('mailouts', MailoutManageViewSet, 'mailout')
router.register('messages', MailoutMessageDetailApiView, 'message')

urlpatterns = [
    path('recipient-create/', RecipientPostApiView.as_view()),
    path('recipient-update/<int:pk>', RecipientPutApiView.as_view()),
    path('recipient-delete/<int:pk>', RecipientDeleteApiView.as_view()),
    path('mailout-create/', MailoutCreateApiView.as_view()),
    path('mailout-list/', MailoutListApiView.as_view()),
    path('mailout-update/<int:pk>', MailoutPatchApiView.as_view()),
    path('mailout-delete/<int:pk>', MailoutDeleteApiView.as_view()),
    path('mailout-info/<int:pk>', MailoutDetailApiView.as_view()),
    path('manage/', include(router.urls)),
]
