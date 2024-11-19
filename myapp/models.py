import json
from django.db import models
from django.contrib.auth.models import User  # If using Django's built-in User model
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from jsonfield import JSONField  # Use this to store JSON data

class CanvasState(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Associate with a user if needed
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=100)  # Field for category
    difficulty = models.CharField(max_length=50)  # Field for difficulty level
    nodes = JSONField()  # Store nodes as JSON
    wires = JSONField()  # Store wire connections as JSON
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class CanvasStateDefend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Associate with a user if needed
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=100)  # Field for category
    difficulty = models.CharField(max_length=50)  # Field for difficulty level
    nodes = JSONField()  # Store nodes as JSON
    wires = JSONField()  # Store wire connections as JSON
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Links score to a user
    score = models.IntegerField()
    date_submitted = models.DateField(auto_now_add=True)  # Stores the date when the score was submitted
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for record creation
    finished = models.BooleanField(default=False)  # Tracks if the user has finished the activity
    category = models.CharField(max_length=255)  # Stores the category of the selected canvas
    correct_submissions = models.IntegerField(default=0)  # Tracks correct submissions
    incorrect_submissions = models.IntegerField(default=0)  # Tracks incorrect submissions

    def __str__(self):
        return f"User: {self.user.username}, Score: {self.score}, Finished: {self.finished}, Category: {self.category}, Correct: {self.correct_submissions}, Incorrect: {self.incorrect_submissions}, Date: {self.date_submitted}"



class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/')
    author = models.CharField(max_length=100)
    date_published = models.DateField()
    url = models.URLField(max_length=300, null=True, blank=True)  # New field for URL
    def __str__(self):
        return self.title

class EmailLog(models.Model):
    recipients = models.TextField()  # To store recipient emails as a comma-separated string
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_new = models.BooleanField(default=True)  # Field to mark if the email is new
    
    def __str__(self):
        return f"Email sent to {self.recipients} at {self.sent_at}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    section = models.CharField(max_length=50)
    program = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True, default='profile_images/default_QBRSs97.jpg')
    is_online = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    accepted_data_privacy = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} Profile"
    
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


