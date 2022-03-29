from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

API_TITLE = 'Notifications API'
API_DESCRIPTION = 'HTTP API for creating and managing mail-outs.'
schema_view = get_schema_view(
    openapi.Info(
        title=API_TITLE,
        default_version='v0.1',
        description=API_DESCRIPTION,
        terms_of_service='https://www.google.com/policies/terms/',
        contact=openapi.Contact(
            name='Dmitry Takmakov',
            url='https://github.com/DmitryTakmakov',
            email='digitalaudiotape5000@gmail.com'
        ),
        license=openapi.License(
            name='The MIT License',
            url='https://opensource.org/licenses/MIT'
        )
    ),
    permission_classes=(permissions.AllowAny,),
    public=True
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('notificationsapp.urls')),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0)),
]
