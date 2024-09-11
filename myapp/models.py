from django.db import models
from django.contrib.auth.models import User  # If using Django's built-in User model
from django.conf import settings

class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    feedback = models.TextField()

    def __str__(self):
        return f"Feedback from {self.email or 'Anonymous'}"