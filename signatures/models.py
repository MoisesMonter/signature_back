# from django.db import models
# from django.utils import timezone
# from django.conf import settings
# from django.contrib.auth.models import User

# class SignatureList(models.Model):
#     owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     start_date = models.DateTimeField(auto_now_add=True)
#     update_date = models.DateTimeField(auto_now=True)
#     end_date = models.DateTimeField(null=True, blank=True)
#     password = models.CharField(max_length=255, blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#     is_completed = models.BooleanField(default=False)
#     n_signature = models.IntegerField(default=0)
    
#     def __str__(self):
#         return self.title

#     def update_n_signature(self):
#         # Atualiza o número de assinaturas válidas
#         self.n_signature = self.signatures.filter(flag__lt=3).count()
#         self.save(update_fields=['n_signature'])

# class Signature(models.Model):
#     signature_list = models.ForeignKey('SignatureList', on_delete=models.CASCADE, related_name='signatures')
#     data = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     flag = models.IntegerField(default=0)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='signatures')

#     def save(self, *args, **kwargs):
#         # Verifica se a lista de assinaturas está ativa, não finalizada e dentro do prazo
#         if not self.signature_list.is_active:
#             raise ValueError("Não é possível adicionar uma assinatura: a lista está inativa.")
        
#         if self.signature_list.is_completed:
#             raise ValueError("Não é possível adicionar uma assinatura: a lista já foi finalizada.")
        
#         if self.signature_list.end_date and self.signature_list.end_date <= timezone.now():
#             raise ValueError("Não é possível adicionar uma assinatura: o prazo da lista expirou.")

#         # Verifica se existe uma assinatura com flag=3 para o mesmo usuário e lista de assinaturas
#         existing_signature = Signature.objects.filter(
#             signature_list=self.signature_list, 
#             user=self.user, 
#             flag=3
#         ).first()

#         if existing_signature and self.pk is None:
#             # Atualiza a assinatura existente ao invés de criar uma nova
#             existing_signature.data = self.data
#             existing_signature.flag = 0
#             existing_signature.created_at = timezone.now()
#             existing_signature.save(update_fields=['data', 'flag', 'created_at'])
#         else:
#             # Salva a nova assinatura ou uma atualização existente
#             super(Signature, self).save(*args, **kwargs)

#         # Atualiza o campo update_date da lista de assinaturas e o número de assinaturas válidas
#         self.signature_list.update_date = timezone.now()
#         self.signature_list.update_n_signature()

#     def delete(self, *args, **kwargs):
#         # Implementa um "soft delete" alterando o flag para 3 e limpando os dados
#         self.data = ""
#         self.flag = 3
#         self.save(update_fields=['data', 'flag'])

#         # Atualiza o número de assinaturas na lista
#         self.signature_list.update_n_signature()

#     def __str__(self):
#         return f'Signature {self.id} for {self.signature_list.title}'


from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class SignatureList(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField(auto_now_add=True)    
    update_date = models.DateTimeField(auto_now=True)
    end_date = models.DateTimeField(null=True, blank=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    n_signature = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def update_n_signature(self):
        self.n_signature = self.signatures.filter(flag__lt=3).count()
        self.save(update_fields=['n_signature'])

    def adjust_signatures_flags(self):
        for signature in self.signatures.exclude(flag=3):
            if not self.is_active and self.is_completed:
                signature.flag = 1  # Finalizado com sucesso
            elif not self.is_active and not self.is_completed:
                signature.flag = 2  # Encerrado
            elif self.is_active and not self.is_completed:
                signature.flag = 0  # Aberto
            signature.save(update_fields=['flag'])


class Signature(models.Model):
    signature_list = models.ForeignKey('SignatureList', on_delete=models.CASCADE, related_name='signatures')
    data = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    flag = models.IntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='signatures')

    def delete(self,*args,**Kwargs):
        self.flag = 3
        self.save()

    def save(self, *args, **kwargs):
        allow_inactive_operations = kwargs.pop('allow_inactive_operations', False)


        if not allow_inactive_operations:
            if not self.signature_list.is_active:
                raise ValueError("Não é possível adicionar ou alterar uma assinatura: a lista está inativa.")
            if self.signature_list.is_completed:
                raise ValueError("Não é possível adicionar ou alterar uma assinatura: a lista já foi finalizada.")
            if self.signature_list.end_date and self.signature_list.end_date <= timezone.now():
                raise ValueError("Não é possível adicionar ou alterar uma assinatura: o prazo da lista expirou.")

        super(Signature, self).save(*args, **kwargs)
        self.signature_list.update_date = timezone.now()
        self.signature_list.update_n_signature()

@receiver(post_save, sender=Signature)
@receiver(post_delete, sender=Signature)
def update_signature_count(sender, instance, **kwargs):
    instance.signature_list.update_n_signature()