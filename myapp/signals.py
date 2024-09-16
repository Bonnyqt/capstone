from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth.signals import user_logged_in, user_logged_out


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(user_logged_in)
def set_user_online(sender, user, request, **kwargs):
    user.userprofile.is_online = True
    user.userprofile.save()

@receiver(user_logged_out)
def set_user_offline(sender, user, request, **kwargs):
    user.userprofile.is_online = False
    user.userprofile.save()