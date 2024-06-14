from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
import debug_toolbar


from AllService_BE import settings

schema_view = get_schema_view(
    openapi.Info(
        title="AllService API",
        default_version="v1"
    ),
    public=True,
    permission_classes=[permissions.AllowAny, ]
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
if settings.DEBUG:
    urlpatterns += [
        path('debug/', include('debug_toolbar.urls')),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)