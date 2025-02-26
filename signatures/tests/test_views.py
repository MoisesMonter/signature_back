from rest_framework.test import APITestCase, force_authenticate
from django.urls import reverse
from django.contrib.auth import get_user_model
from signatures.models import SignatureList, Signature
from rest_framework.authtoken.models import Token
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()
class SignatureListViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="owner@test.com")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.signature_list = SignatureList.objects.create(
            owner=self.user,
            title="Lista de Teste",
            description="Descrição da Lista"
        )

    def test_update_state(self):
        url = reverse('signaturelist-update-state', args=[self.signature_list.id])
        data = {"is_active": False, "is_completed": True}
        response = self.client.patch(url, data, format='json')  # Adicione format='json'
        self.assertEqual(response.status_code, 200)

        # Atualiza o objeto signature_list do banco de dados
        self.signature_list.refresh_from_db()
        self.assertFalse(self.signature_list.is_active)
        self.assertTrue(self.signature_list.is_completed)

    def test_update_state_inativo_flag_Finalizado(self):
        # Cria assinatura antes de atualizar o estado
        signature = Signature.objects.create(signature_list=self.signature_list, user=self.user, flag=0)
        
        url = reverse('signaturelist-update-state', args=[self.signature_list.id])
        data = {"is_active": False, "is_completed": True}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        
        signature.refresh_from_db()
        self.assertEqual(signature.flag, 1)


    def test_lista_assinatura_com_password(self):
        self.signature_list.password = "secret"
        self.signature_list.save()
        
        url = reverse('signaturelist-public-view', args=[self.signature_list.id])
        response = self.client.get(url, {'password': 'secret'})
        self.assertEqual(response.status_code, 200)

    def test_lista_assinatura_com_password_errada(self):
        self.signature_list.password = "secret"
        self.signature_list.save()
        
        url = reverse('signaturelist-public-view', args=[self.signature_list.id])
        response = self.client.get(url, {'password': 'wrong'})
        self.assertEqual(response.status_code, 403)

    def test__lista_assinatura_sem_password(self):
        self.signature_list.password = None
        self.signature_list.save()
        
        url = reverse('signaturelist-public-view', args=[self.signature_list.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


    def test_combine_assinaturas_lista_vazia(self):
        url = reverse('signaturelist-combine-signatures', args=[self.signature_list.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"error": "Você precisa ter ao menos uma assinatura."})
        
    def test_combine_assinaturas_lista_com_assinaturas(self):

        Signature.objects.create(
            signature_list=self.signature_list,
            user=self.user,
            data="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        )
        
        url = reverse('signaturelist-combine-signatures', args=[self.signature_list.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')

class SignatureViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@test.com")
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.signature_list = SignatureList.objects.create(
            owner=self.user,
            title="Lista de Teste",
            description="Descrição da Lista"
        )

    def test_criando_assinatura(self):
        url = reverse('signature-list')
        data = {
            "signature_list": self.signature_list.id,
            "data": "base64_image_data"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_my_participations(self):
        # Cria uma assinatura para o usuário
        Signature.objects.create(signature_list=self.signature_list, user=self.user, data="base64_image_data")

        url = reverse('signature-my-participations')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)