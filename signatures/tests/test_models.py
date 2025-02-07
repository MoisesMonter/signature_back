from django.test import TestCase
from django.contrib.auth import get_user_model
from signatures.models import SignatureList, Signature
from django.utils import timezone
from django.core.exceptions import ValidationError

User = get_user_model()

class SignatureListModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="owner@test.com")
        self.signature_list = SignatureList.objects.create(
            owner=self.user,
            title="Lista de Teste",
            description="Descrição da Lista"
        )

    def test_update_n_assinaturas(self):

        Signature.objects.create(signature_list=self.signature_list, user=self.user, flag=0)
        Signature.objects.create(signature_list=self.signature_list, user=self.user, flag=1)
        Signature.objects.create(signature_list=self.signature_list, user=self.user, flag=2)

        self.signature_list.update_n_signature()
        self.assertEqual(self.signature_list.n_signature, 3)

    def test_lista_assinatura_modificado_em_Aberto(self):
        signature = Signature.objects.create(signature_list=self.signature_list, user=self.user, flag=0)

        self.signature_list.is_active = True
        self.signature_list.is_completed = False
        self.signature_list.save()

        # Ajusta as flags das assinaturas, permitindo operações em listas inativas
        self.signature_list.adjust_signatures_flags()

        # Atualiza a assinatura com allow_inactive_operations=True
        signature.refresh_from_db()
        signature.save(allow_inactive_operations=True) 


        self.assertEqual(signature.flag, 0)

    def test_salvar_assinatura_quando_lista_em_Aberto(self):

        signature_list = SignatureList.objects.create(
            owner=self.user,
            title="Lista em Aberto",
            description="Lista de Teste em Aberto",
            is_active=True,  
            is_completed=False  
        )

        signature = Signature.objects.create(
            signature_list=signature_list,
            user=self.user,
            data="assinatura"
        )

        self.assertEqual(signature.data, "assinatura")
        self.assertEqual(signature.signature_list, signature_list)
        self.assertEqual(signature.user, self.user)

        signature.data = "nova_assinatura"
        signature.save()
        
        signature.refresh_from_db()
        self.assertEqual(signature.data, "nova_assinatura")

    def test_salvar_quando_lista_Inativa(self):
        self.signature_list.is_active = False
        self.signature_list.save()
        
        signature = Signature(signature_list=self.signature_list, user=self.user, data="test")
        signature.save(allow_inactive_operations=True)  # Não deve lançar erro
        self.assertIsNotNone(signature.id)

    def test_falha_salvar_assinatura_quando_lista_Concluido_e_Aberto(self):
  
        signature_list = SignatureList.objects.create(
            owner=self.user,
            title="Lista Ativa e Concluída",
            description="Lista de Teste Ativa e Concluída",
            is_active=True, 
            is_completed=True 
        )

        with self.assertRaises(ValueError) as context:
            Signature.objects.create(
                signature_list=signature_list,
                user=self.user,
                data="assinatura"
            )

        self.assertEqual(
            str(context.exception),
            "Não é possível adicionar ou alterar uma assinatura: a lista já foi finalizada."
        )
    
    def test_falha_salvar_assinatura_quando_lista_inativo(self):
        # Cria uma lista de assinaturas
        signature_list = SignatureList.objects.create(
            owner=self.user,
            title="Lista Inativa",
            description="Lista de Teste Inativa",
            is_active=False,  # Lista inativa
            is_completed = False
        )

        # Tenta criar uma assinatura em uma lista inativa
        with self.assertRaises(ValueError) as context:
            Signature.objects.create(
                signature_list=signature_list,
                user=self.user,
                data="assinatura"
            )
        
        # Verifica a mensagem de erro
        self.assertEqual(
            str(context.exception),
            "Não é possível adicionar ou alterar uma assinatura: a lista está inativa."
        )

    def test_falha_salvar_assinatura_quando_Concluido(self):
        signature_list = SignatureList.objects.create(
            owner=self.user,
            title="Lista Concluída",
            description="Lista de Teste Concluída",
            is_active=False, 
            is_completed=True
        )

        with self.assertRaises(ValueError) as context:
            Signature.objects.create(
                signature_list=signature_list,
                user=self.user,
                data="assinatura"
            )
        
        self.assertEqual(
            str(context.exception),
            "Não é possível adicionar ou alterar uma assinatura: a lista já foi finalizada."
        )

    def test_finalizar_lista_sem_assinaturas(self):
        # Cria uma lista de assinaturas vazia
        empty_signature_list = SignatureList.objects.create(
            owner=self.user,
            title="Lista Vazia",
            description="Uma lista sem assinaturas"
        )
        

        self.signature_list.is_active = False
        self.signature_list.is_completed = True
        self.signature_list.save()
        

        self.assertFalse(empty_signature_list.is_completed)

    def test_titlulo_maximo_length(self):

        valid_title = "a" * 255

        empty_signature_list = SignatureList.objects.create(
            owner=self.user,
            title="a"*255,
            description="Uma lista sem assinaturas"
        )


        self.assertEqual(len(valid_title), 255)
        self.assertEqual(empty_signature_list.title, valid_title)

    
    def test_title_estourado_length(self):
        valid_title = "a" * 255

        empty_signature_list = SignatureList.objects.create(
            owner=self.user,
            title="a"*256,
            description="Uma lista sem assinaturas"
        )


        self.assertEqual(len(valid_title), 255)
        self.assertNotEqual(len(empty_signature_list.title), len(valid_title))


    def test_title_abaixo_length(self):
        valid_title = "a" * 255

        empty_signature_list = SignatureList.objects.create(
            owner=self.user,
            title="a"*25,
            description="Uma lista sem assinaturas"
        )

        self.assertEqual(len(valid_title), 255)
        self.assertTrue(len(empty_signature_list.title) < len(valid_title))

class SignatureModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@test.com")
        self.signature_list = SignatureList.objects.create(
            owner=self.user,
            title="Lista de Teste",
            description="Descrição da Lista"
        )

    def test_salvar_assinatura_quando_lista_inativa(self):
        self.signature_list.is_active = False
        self.signature_list.save()

        # Tenta criar uma assinatura
        with self.assertRaises(ValueError):
            Signature.objects.create(signature_list=self.signature_list, user=self.user, data="assinatura")

    def test_deletar_assinatura(self):
        signature = Signature.objects.create(signature_list=self.signature_list, user=self.user, data="assinatura")
        signature.delete()
        signature.refresh_from_db()
        self.assertEqual(signature.flag, 3)  # Flag de deletado