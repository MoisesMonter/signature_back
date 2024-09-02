# ata_model/models.py
from django.conf import settings
from django.db import models
from signatures.models import SignatureList
from django.utils import timezone

class Ata(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='atas')
    title = models.CharField(max_length=255, blank=True, default="")
    text = models.TextField()
    signature_list = models.ForeignKey(SignatureList, on_delete=models.SET_NULL, null=True, blank=True, related_name='atas') 
    created_at = models.DateTimeField(auto_now_add=True)  

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = f"Modelo ATA {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
