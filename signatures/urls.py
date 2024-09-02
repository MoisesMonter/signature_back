from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SignatureListViewSet, SignatureViewSet

router = DefaultRouter()
router.register(r'signature_lists', SignatureListViewSet)
router.register(r'signatures', SignatureViewSet)

urlpatterns = [
    path('', include(router.urls)),
]