from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('api/auth/', include('users.urls')),
    path('api/cabinets/', include('cabinets.urls')),

    path('admin/', admin.site.urls),
    url(r'^files/', include('db_file_storage.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# handler404 = 'app.views.handler404'
