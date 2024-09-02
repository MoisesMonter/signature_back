from django.urls import include, path
from .router_user import router as user_router
from .router_user_external_api import urlpatterns as external_api_urls

urlpatterns = [
    path('', include(user_router.urls)),
    path('', include(external_api_urls)),
]
