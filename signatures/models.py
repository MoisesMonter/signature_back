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
                if self.signature_list.is_completed:
                    raise ValueError("Não é possível adicionar ou alterar uma assinatura: a lista já foi finalizada.")
                else:
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