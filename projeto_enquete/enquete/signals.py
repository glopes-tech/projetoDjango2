from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Aluno

@receiver(post_save, sender=User)
def create_or_update_aluno_profile(sender, instance, created, **kwargs):
    if created:
        Aluno.objects.create(user=instance, nome=instance.username) 
    #instance.aluno.save()
pass   