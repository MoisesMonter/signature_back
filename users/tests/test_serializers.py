from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from ..serializers import UserSerializer, LimitedUserSerializer
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()

class UserSerializerTest(APITestCase):
    def test_serializador_completo(self):
        user = User.objects.create(
            user_id="github_456",
            email="user@test.com",
            first_name="Fulano",
            my_signature="Assinatura secreta"
        )
        serializer = UserSerializer(user)
        self.assertEqual(serializer.data["my_signature"], "Assinatura secreta")
        self.assertIn("is_active", serializer.data)

    def test_serializador_limitado(self):
        user = User.objects.create(email="limited@test.com")
        serializer = LimitedUserSerializer(user)
        
        self.assertNotIn("my_signature", serializer.data)
        self.assertIsNone(serializer.data["photo_url"])