from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    user_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    photo_url = models.URLField(max_length=200, null=True, blank=True)
    is_owner = models.BooleanField(default=False)
    my_signature = models.TextField(null=True, blank=True) 

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()

    def save(self, *args, **kwargs):
        if self.user_id and not self.username:
            self.username = self.user_id
        super(User, self).save(*args, **kwargs)