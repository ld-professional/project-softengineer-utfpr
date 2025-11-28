from django.contrib import admin
from django.urls import path, include


# para ter as fotos
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('account/',include('account.urls')),
    path('clientes/',include('clientes.urls')),
    path('barbeiro/',include('barbeiro.urls')),

    path('',include('global.urls')),
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
