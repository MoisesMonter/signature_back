from rest_framework import serializers
from .models import Ata

class AtaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ata
        fields = ['id', 'user', 'title', 'text', 'signature_list', 'created_at']
        read_only_fields = ['user', 'created_at']
        extra_kwargs = {
            'title': {'required': False, 'allow_blank': True, 'default': ''},
            'signature_list': {'required': False, 'allow_null': True}
        }
