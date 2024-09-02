from django.urls import path, include
from .View import urlpatterns as user_urls
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include(user_urls)),  
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


