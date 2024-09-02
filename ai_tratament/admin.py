from django.contrib import admin
from .models import ProcessedData

@admin.register(ProcessedData)
class ProcessedDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'source_id', 'source_app', 'created_at', 'processed_text')
    search_fields = ('user__username', 'source_app')
    list_filter = ('created_at', 'source_app')
