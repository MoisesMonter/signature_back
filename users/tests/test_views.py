from django.urls import reverse
from rest_framework.test import APITestCase, force_authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()

class UserViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="admin@test.com",
            user_id="admin_123",
            is_active=True
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_listar_usuarios_com_dados_limitados(self):
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("my_signature", response.data[0])

    def test_endpoint_me(self):
        url = reverse('user-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("my_signature", response.data)

    def test_desativar_usuario_via_delete(self):
        url = reverse('user-me')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_criar_usuario_sem_photo_url(self):
        data = {
            "user_id": "new_user",
            "email": "new@test.com",
            "username": "new_user", 
            "first_name": "Novo Usuário"
        }
        url = reverse('user-list')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        # self.assertNotIn("photo_url", response.data[0])  