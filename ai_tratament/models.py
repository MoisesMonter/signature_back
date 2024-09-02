# ai_tratament/models.py
from django.conf import settings
from django.db import models

class ProcessedData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='processed_data')
    source_id = models.PositiveIntegerField()
    source_app = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_text = models.TextField()

    def __str__(self):
        return f'Processed data from {self.source_app} (ID: {self.source_id})'
