import json
from django.db import models
from django.contrib.auth.models import User  # If using Django's built-in User model
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from jsonfield import JSONField  # Use this to store JSON data

class Course(models.Model):
    CourseCode = models.CharField(max_length=20)
    CourseName = models.CharField(max_length=100)
    CourseDesc = models.TextField()
    Program = models.CharField(max_length=100)
    Section = models.CharField(max_length=50)
    published_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.CourseName

class Analysis(models.Model):
    bar_graph = models.TextField(null=True, blank=True)  # Analysis for bar graph
    pie_graph = models.TextField(null=True, blank=True)  # Analysis for pie chart
    areachart_graph = models.TextField(null=True, blank=True)
    split_graph = models.TextField(null=True, blank=True)  # Analysis for area chart
    data_checksum = models.CharField(max_length=32)  # Store the checksum (MD5 hash)
    challenge_definition = models.TextField(null=True, blank=True)  # Clever definition of the challenge title
    created_at = models.DateTimeField(auto_now_add=True)

class StudentAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link analysis to a specific user
    bar_graph = models.TextField(null=True, blank=True)
    pie_graph = models.TextField(null=True, blank=True)
    areachart_graph = models.TextField(null=True, blank=True)
    split_graph = models.TextField(null=True, blank=True)
    data_checksum = models.CharField(max_length=32)
    challenge_definition = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CanvasState(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=50)
    title_definition = models.CharField(max_length=200)
    canvas_section = models.CharField(max_length=50)
    canvas_time = models.IntegerField()
    due_date = models.DateTimeField(null=True, blank=True)  # New field for the deadline
    nodes = JSONField()
    wires = JSONField()
    canvas_scenario = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class CanvasStateDefend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Associate with a user if needed
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=100)  # Field for category
    difficulty = models.CharField(max_length=50)
    title_definition = models.CharField(max_length=200)
    canvas_section = models.CharField(max_length=50)  # Field for difficulty level
    canvas_time = models.IntegerField()  # Field for canvas timer (in seconds)
    nodes = JSONField()  # Store nodes as JSON
    wires = JSONField()  # Store wire connections as JSON
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CanvasInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Links interaction to a user
    canvas_state = models.ForeignKey(CanvasState, null=True, blank=True, on_delete=models.CASCADE)  # Links interaction to a specific CanvasState
    canvas_state_defend = models.ForeignKey(CanvasStateDefend, null=True, blank=True, on_delete=models.CASCADE)  # Links interaction to a specific CanvasStateDefend
    clicked_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the canvas was clicked
    locked = models.BooleanField(default=False)  # Whether the challenge was locked at the time of click
    access_count = models.PositiveIntegerField(default=0)  # Tracks number of accesses at the time of click

    def __str__(self):
        # Return which canvas the user interacted with
        if self.canvas_state:
            return f"User: {self.user.username}, Canvas: {self.canvas_state.title}, Clicked at: {self.clicked_at}"
        elif self.canvas_state_defend:
            return f"User: {self.user.username}, Canvas: {self.canvas_state_defend.title}, Clicked at: {self.clicked_at}"
        return f"User: {self.user.username}, Clicked at: {self.clicked_at}"

class Score(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    date_submitted = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    finished = models.BooleanField(default=False)
    category = models.CharField(max_length=255)
    correct_submissions = models.IntegerField(default=0)
    incorrect_submissions = models.IntegerField(default=0)
    canvas_state_title = models.CharField(max_length=100, null=True, blank=True)
    closed_by_user = models.BooleanField(default=False)
    canvas_explanation = models.TextField(null=True, blank=True)
    
    # New fields for total score and total correct answers possible
    total_possible_score = models.IntegerField(default=0)  # Total score possible for the challenge
    total_possible_correct_answers = models.IntegerField(default=0)  # Total correct answers possible for the challenge

    def __str__(self):
        return f"User: {self.user.username}, Score: {self.score}, Finished: {self.finished}, Category: {self.category}, Correct: {self.correct_submissions}, Incorrect: {self.incorrect_submissions}, Date: {self.date_submitted}, Canvas Title: {self.canvas_state_title}, Total Score Possible: {self.total_possible_score}, Total Correct Answers Possible: {self.total_possible_correct_answers}"

class UserSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    window_open = models.BooleanField(default=False)

    def __str__(self):
        return f"Session for {self.user.username}"

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
    section = models.CharField(max_length=255, null=False, blank=False)  # Ensure it's not null
    program = models.CharField(max_length=255, null=True, blank=True)   # Optional fields
    course_code = models.CharField(max_length=255, null=True, blank=True)
    course_name = models.CharField(max_length=255, null=True, blank=True)
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



class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)  # User who performed the action
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)  # Type of action
    model_name = models.CharField(max_length=100)  # The model on which action was performed
    model_instance_id = models.IntegerField()  # ID of the affected instance
    field_name = models.CharField(max_length=100, null=True, blank=True)  # Name of the field that was changed (if applicable)
    old_value = models.TextField(null=True, blank=True)  # Old value before the change
    new_value = models.TextField(null=True, blank=True)  # New value after the change
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of the action

    def __str__(self):
        return f"{self.action_type} on {self.model_name} by {self.user.username if self.user else 'System'} at {self.created_at}"
