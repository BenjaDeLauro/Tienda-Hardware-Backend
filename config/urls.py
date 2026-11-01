from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from catalogo.vistas_web import BienvenidaView


urlpatterns = [
    path('', BienvenidaView.as_view(), name='inicio'),
    path('usuarios/', include('usuarios.urls')),
    path('catalogo/', include('catalogo.urls_web')),
    path('api/auth/', include('usuarios.urls_api')),
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
    path('api/', include('catalogo.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
