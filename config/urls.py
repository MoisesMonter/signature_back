from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/signatures/', include('signatures.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    path('auth/', include('allauth.urls')),
    path('api/users/', include('users.urls')),
    path('api/docs/ata/', include('ata_model.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'), 
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'), 
    # path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'), 
]
