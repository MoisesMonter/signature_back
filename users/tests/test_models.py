from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class UserModelTest(TestCase):
    def test_criar_usuario_com_user_id(self):
        # Testa se o username é definido automaticamente pelo user_id
        user = User.objects.create(
            user_id="google_123",
            email="test@example.com",
            first_name="Teste"
        )
        self.assertEqual(user.username, "google_123")

    def test_desativar_usuario_ao_deletar(self):
        # Testa uma conta usando rota delete para validar se foi apenas desativada
        user = User.objects.create(email="test@example.com")
        user.delete()
        user.refresh_from_db()
        self.assertFalse(user.is_active)


    def test_falha_cadastro_email(self):
        # Criando um usuário sem o campo email (obrigatório) esperando falha
        user = User(user_id="2", first_name="User_Test",email=None)
        with self.assertRaises(ValidationError):
            user.full_clean()