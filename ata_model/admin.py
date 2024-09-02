# ata_model/admin.py
from django.contrib import admin
from .models import Ata

class AtaAdmin(admin.ModelAdmin):
    list_display = ('title','id', 'user', 'signature_list', 'created_at')
    search_fields = ('title', 'user__username', 'signature_list__name')
    list_filter = ('created_at', 'user')

admin.site.register(Ata, AtaAdmin)
