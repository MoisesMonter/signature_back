from django.contrib import admin
from .models import SignatureList, Signature

class SignatureInline(admin.TabularInline):
    model = Signature
    extra = 0
    readonly_fields = ('data', 'created_at')

class SignatureListAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'owner', 'n_signatures', 'id')
    search_fields = ('title', 'owner__username')
    list_filter = ('start_date', 'owner')
    inlines = [SignatureInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('signatures', 'owner')

    def n_signatures(self, obj):
        return obj.signatures.count()
    n_signatures.short_description = 'Number of Signatures'

class SignatureAdmin(admin.ModelAdmin):
    list_display = ('id', 'signature_list_id', 'signature_list_name', 'user', 'flag', 'created_at')
    search_fields = ('signature_list__id', 'user__username')
    list_filter = ('created_at', 'flag')
    readonly_fields = ('created_at',)
    exclude = ('data',) 


    fields = ('signature_list', 'user', 'flag')

    def signature_list_id(self, obj):
        return obj.signature_list.id

    def signature_list_name(self, obj):
        return obj.signature_list.title

    signature_list_id.short_description = 'Signature List ID'
    signature_list_name.short_description = 'Signature List Name'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('signature_list', 'user')


admin.site.register(SignatureList, SignatureListAdmin)
admin.site.register(Signature, SignatureAdmin)
