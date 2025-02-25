from rest_framework.test import APITestCase
from signatures.models import SignatureList
from signatures.serializers import SignatureListSerializer
from django.contrib.auth import get_user_model
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()

class SignatureListSerializerTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="owner@test.com")
        self.signature_list = SignatureList.objects.create(
            owner=self.user,
            title="Lista de Teste",
            description="Descrição da Lista"
        )

    def test_serialize_lista_assinatura(self):
        serializer = SignatureListSerializer(self.signature_list)
        self.assertEqual(serializer.data['title'], "Lista de Teste")
        self.assertEqual(serializer.data['owner'], self.user.username)

    def test_criando_lista_assinatura(self):
        data = {
            "title": "Nova Lista",
            "description": "Nova Descrição",
            "password": "senha123"
        }
        serializer = SignatureListSerializer(data=data, context={'request': self.user})
        self.assertTrue(serializer.is_valid())
        signature_list = serializer.save(owner=self.user)
        self.assertEqual(signature_list.title, "Nova Lista")