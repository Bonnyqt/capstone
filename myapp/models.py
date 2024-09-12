from django.db import models
from django.contrib.auth.models import User  # If using Django's built-in User model
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone


class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)  


    def save(self, *args, **kwargs):
        if not self.pk:  # Only hash password when creating a new user
            self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    

class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    feedback = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_new = models.BooleanField(default=True)  # Add this field to track if feedback is new

    def __str__(self):
        return f"Feedback from {self.email or 'Anonymous'}"
    