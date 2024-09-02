# from rest_framework import serializers
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class LimitedUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'first_name', 'email', 'photo_url']  # Apenas os campos permitidos para outros usuários

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'user_id', 'username', 'email', 'first_name', 'photo_url', 'is_active', 'my_signature']  



from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class LimitedUserSerializer(serializers.ModelSerializer):
    photo_url = serializers.CharField(default='http://cdn-icons-png.flaticon.com/512/3106/3106807.png', allow_null=True)
    class Meta:
        model = User
        fields = ['id', 'first_name', 'email', 'photo_url']  # Apenas os campos permitidos para outros usuários

class UserSerializer(serializers.ModelSerializer):
    photo_url = serializers.CharField(default='http://cdn-icons-png.flaticon.com/512/3106/3106807.png', allow_null=True)
    class Meta:
        model = User
        fields = ['id', 'user_id', 'username', 'email', 'first_name', 'photo_url', 'is_active', 'my_signature']  
        extra_kwargs = {
            'my_signature': {'required': False}
        }