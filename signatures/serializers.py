from rest_framework import serializers
from .models import SignatureList, Signature
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'email', 'photo_url']
        

class UserSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'email', 'photo_url'] 

class SignatureSerializer(serializers.ModelSerializer):
    user = UserSignatureSerializer(read_only=True)  # Inclui o usuário relacionado à assinatura
    title = serializers.CharField(source='signature_list.title', read_only=True)
    update_date = serializers.DateTimeField(source='signature_list.update_date', read_only=True)

    class Meta: 
        model = Signature
        fields = ['id', 'signature_list', 'data', 'created_at', 'user','flag', 'title', 'update_date']  # Inclua 'user' nos fields



class SignatureListSerializer(serializers.ModelSerializer):
    signatures = SignatureSerializer(many=True, read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')
    password = serializers.CharField(required=False, allow_blank=True) 

    class Meta:
        model = SignatureList
        fields = ['id', 'owner', 'title', 'description', 'start_date', 'update_date', 'end_date', 'signatures', 'n_signature', 'password','is_completed','is_active']
        read_only_fields = ['owner', 'start_date', 'update_date', 'signatures']

    def get_password(self, obj):
        request = self.context.get('request')
        if request and request.user == obj.owner:
            return obj.password
        return None  
    def create(self, validated_data):
        return super().create(validated_data)



class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'email', 'photo_url']  


class PublicSignatureListSerializer(serializers.ModelSerializer):
    owner = PublicUserSerializer(read_only=True)  


    class Meta:
        model = SignatureList
        fields = ['id', 'owner', 'title', 'description', 'start_date', 'end_date']



class SignatureSerializer_transparence(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)  
    title = serializers.CharField(source='signature_list.title', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    update_date = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Signature
        fields = ['id', 'title', 'flag', 'created_at', 'update_date', 'owner']

