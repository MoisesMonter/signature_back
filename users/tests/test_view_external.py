from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()
class LoginAPITest(APITestCase):
    def test_login_com_usuario_existente(self):
        User.objects.create(
            user_id="existing_user",
            email="exist@test.com",
            is_active=True
        )
        data = {
            "user_id": "existing_user",
            "email": "exist@test.com",
            "first_name": "Atualizado"
        }
        url = reverse('login')  # Nome correto da rota
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, data)

    def test_criar_usuario_via_login(self):
        data = {
            "email": "new@test.com",
            "first_name": "Novo Usuário",
            "photo_url": "http://nova-foto.jpg"
        }
        url = reverse('login')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(email="new@test.com").exists())

    def test_validar_email_obrigatorio(self):
        data = {"user_id": "sem_email"}
        url = reverse('login') 
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)