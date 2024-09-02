# ata_model/urls.py
from django.urls import path
from .views import AtaCreateView

urlpatterns = [
    path('create/', AtaCreateView.as_view(), name='ata_create'),
]