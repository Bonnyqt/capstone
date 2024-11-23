from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth.signals import user_logged_in, user_logged_out
import json
from datetime import date
import logging
from tkinter import Canvas
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.views import View
from .models import CanvasStateDefend, Feedback
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.utils.html import strip_tags
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.utils import timezone
from pytz import timezone as pytz_timezone  
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile
from .forms import UserProfileForm
from django.http import HttpResponseNotFound
from django.contrib.auth.models import User
from django.db.models.functions import TruncMonth
from django.db.models import Count
from .models import EmailLog
from .models import BlogPost
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import EmailLog
from collections import Counter
import random
import string
from django.db.models import Q
from .models import CanvasState
from django.views.decorators.http import require_POST
from .models import Score 
from django.utils.timezone import now
from django.db import models
from .models import UserSession
import openai
from .models import Analysis
import hashlib
from django.db.models.functions import TruncMonth
from .models import Course
import pandas as pd
from django.http import HttpResponse
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from .models import ActivityLog
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.signals import user_logged_out


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




@receiver(pre_save, sender=User)
def log_user_update(sender, instance, **kwargs):
    if instance.pk:  # Check if the user already exists (i.e., it's an update)
        try:
            old_instance = User.objects.get(pk=instance.pk)
            # Compare fields to detect changes
            for field in instance._meta.fields:
                field_name = field.name
                old_value = getattr(old_instance, field_name)
                new_value = getattr(instance, field_name)
                if old_value != new_value:
                    ActivityLog.objects.create(
                        user=instance,
                        action_type='UPDATE',
                        model_name='User',
                        model_instance_id=instance.pk,
                        field_name=field_name,
                        old_value=str(old_value),
                        new_value=str(new_value),
                    )
        except User.DoesNotExist:
            pass

@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            user=instance,
            action_type='CREATE',
            model_name='User',
            model_instance_id=instance.pk,
        )

@receiver(pre_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    ActivityLog.objects.create(
        user=instance,
        action_type='DELETE',
        model_name='User',
        model_instance_id=instance.pk,
    )

@receiver(pre_save, sender=Score)
def log_score_update(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Score.objects.get(pk=instance.pk)
            for field in instance._meta.fields:
                field_name = field.name
                old_value = getattr(old_instance, field_name)
                new_value = getattr(instance, field_name)
                if old_value != new_value:
                    ActivityLog.objects.create(
                        user=instance.user,
                        action_type='UPDATE',
                        model_name='Score',
                        model_instance_id=instance.pk,
                        field_name=field_name,
                        old_value=str(old_value),
                        new_value=str(new_value),
                    )
        except Score.DoesNotExist:
            pass

@receiver(post_save, sender=Score)
def log_score_creation(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            user=instance.user,
            action_type='CREATE',
            model_name='Score',
            model_instance_id=instance.pk,
        )

@receiver(pre_delete, sender=Score)
def log_score_deletion(sender, instance, **kwargs):
    ActivityLog.objects.create(
        user=instance.user,
        action_type='DELETE',
        model_name='Score',
        model_instance_id=instance.pk,
    )


@receiver(pre_save, sender=CanvasState)
def log_canvas_state_update(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = CanvasState.objects.get(pk=instance.pk)
            for field in instance._meta.fields:
                field_name = field.name
                old_value = getattr(old_instance, field_name)
                new_value = getattr(instance, field_name)
                if old_value != new_value:
                    ActivityLog.objects.create(
                        user=instance.user,
                        action_type='UPDATE',
                        model_name='CanvasState',
                        model_instance_id=instance.pk,
                        field_name=field_name,
                        old_value=str(old_value),
                        new_value=str(new_value),
                    )
        except CanvasState.DoesNotExist:
            pass

@receiver(post_save, sender=CanvasState)
def log_canvas_state_creation(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            user=instance.user,
            action_type='CREATE',
            model_name='CanvasState',
            model_instance_id=instance.pk,
        )

@receiver(pre_delete, sender=CanvasState)
def log_canvas_state_deletion(sender, instance, **kwargs):
    ActivityLog.objects.create(
        user=instance.user,
        action_type='DELETE',
        model_name='CanvasState',
        model_instance_id=instance.pk,
    )
def get_user_activity_logs(user_id):
    """
    Retrieve activity logs for a specific user.
    """
    user = get_object_or_404(User, id=user_id)
    return ActivityLog.objects.filter(user=user).order_by('-created_at')
def calculate_total_score(user_id):
    """
    Calculate the total score for a specific user.
    """
    scores = Score.objects.filter(user_id=user_id)
    total_score = scores.aggregate(total=models.Sum('score'))['total'] or 0
    return total_score

def canvas_state_usage_count(canvas_title):
    """
    Count how many times a CanvasState has been referenced in the Score model.
    """
    return Score.objects.filter(canvas_state_title=canvas_title).count()
def get_recent_feedback(limit=10):
    """
    Retrieve the most recent feedback submissions.
    """
    return Feedback.objects.filter(is_new=True).order_by('-created_at')[:limit]

def get_email_logs_for_user(user_id):
    """
    Get all email logs for a specific user.
    """
    return EmailLog.objects.filter(sent_by_id=user_id).order_by('-sent_at')

def update_user_profile(user_id, course_code=None, program=None, profile_image=None):
    """
    Update the user's profile details.
    """
    profile = UserProfile.objects.get(user_id=user_id)
    if course_code:
        profile.course_code = course_code
    if program:
        profile.program = program
    if profile_image:
        profile.profile_image = profile_image
    profile.save()
    return profile

def get_courses_by_program(program_name):
    """
    Retrieve all courses for a given program.
    """
    return Course.objects.filter(Program__iexact=program_name)

def get_canvas_analysis(canvas_title):
    """
    Get analysis details for a canvas.
    """
    canvas_state = CanvasState.objects.filter(title=canvas_title).first()
    if not canvas_state:
        return None
    return Analysis.objects.filter(data_checksum=canvas_state.title).first()

def mark_feedback_as_read(feedback_id):
    """
    Mark a feedback submission as read.
    """
    feedback = Feedback.objects.get(id=feedback_id)
    feedback.is_new = False
    feedback.save()
    return feedback

def create_user_session(user_id):
    """
    Create a session for a user if it doesn't already exist.
    """
    session, created = UserSession.objects.get_or_create(user_id=user_id)
    session.window_open = True
    session.save()
    return session

def reset_user_scores(user_id):
    """
    Reset all scores for a user to zero.
    """
    Score.objects.filter(user_id=user_id).update(score=0, correct_submissions=0, incorrect_submissions=0, finished=False)

def get_blog_posts_by_author(author_name):
    """
    Fetch all blog posts by a specific author.
    """
    return BlogPost.objects.filter(author__iexact=author_name).order_by('-date_published')

def get_challenge_difficulty_stats():
    """
    Get statistics about challenges grouped by difficulty.
    """
    return CanvasState.objects.values('difficulty').annotate(total=models.Count('difficulty'))

def get_recent_canvas_states(limit=10):
    """
    Get the most recent canvas states.
    """
    return CanvasState.objects.all().order_by('-created_at')[:limit]

def log_user_action(user, action_type, model_name, field_name=None, old_value=None, new_value=None):
    """
    Log a user's action.
    """
    ActivityLog.objects.create(
        user=user,
        action_type=action_type,
        model_name=model_name,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value
    )
def get_feedback_summary():
    """
    Get a summary of feedback, including counts of new and read feedback.
    """
    return {
        'new_feedback_count': Feedback.objects.filter(is_new=True).count(),
        'read_feedback_count': Feedback.objects.filter(is_new=False).count(),
    }
def get_most_active_users(limit=10):
    """
    Get the most active users based on the number of activity logs.
    """
    return User.objects.annotate(activity_count=models.Count('activitylog')).order_by('-activity_count')[:limit]

from django.core.mail import send_mass_mail

def send_bulk_emails(subject, body, recipient_list, sent_by):
    """
    Send bulk emails and log them in the EmailLog model.
    """
    emails = [(subject, body, 'noreply@example.com', [recipient]) for recipient in recipient_list]
    send_mass_mail(emails)
    
    # Log the email
    EmailLog.objects.create(
        recipients=", ".join(recipient_list),
        subject=subject,
        body=body,
        sent_by=sent_by
    )
def get_courses_by_section(section_name):
    """
    Retrieve all courses associated with a specific section.
    """
    return Course.objects.filter(Section__iexact=section_name)
def get_average_scores_by_category():
    """
    Get average scores grouped by category.
    """
    return Score.objects.values('category').annotate(average_score=models.Avg('score')).order_by('-average_score')
from datetime import timedelta
from django.utils.timezone import now

def archive_old_canvas_states(days=30):
    """
    Archive canvas states older than a given number of days.
    """
    cutoff_date = now() - timedelta(days=days)
    old_canvas_states = CanvasState.objects.filter(created_at__lt=cutoff_date)
    # Perform archival logic (e.g., move to a backup table or mark as archived)
    return old_canvas_states.update(is_archived=True)  # Assuming an `is_archived` field exists
def generate_bar_chart_data():
    """
    Generate data for a bar chart showing scores across categories.
    """
    data = Score.objects.values('category').annotate(total_score=models.Sum('score'))
    return [{'category': item['category'], 'total_score': item['total_score']} for item in data]



def count_challenges_by_difficulty():
    """
    Count total challenges grouped by difficulty.
    """
    return CanvasState.objects.values('difficulty').annotate(total=models.Count('id')).order_by('difficulty')
def is_canvas_title_unique(user_id, title):
    """
    Check if a canvas title is unique for the given user.
    """
    return not CanvasState.objects.filter(user_id=user_id, title__iexact=title).exists()
def get_active_users():
    """
    Get all users with an active session.
    """
    return User.objects.filter(usersession__window_open=True)
from datetime import timedelta

def get_latest_blog_posts(days=7):
    """
    Retrieve blog posts published within the last 'days' days.
    """
    cutoff_date = now() - timedelta(days=days)
    return BlogPost.objects.filter(date_published__gte=cutoff_date).order_by('-date_published')
def get_unfinished_scores(user_id):
    """
    Get all unfinished scores for a user.
    """
    return Score.objects.filter(user_id=user_id, finished=False)
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Log user login activity.
    """
    ActivityLog.objects.create(
        user=user,
        action_type='LOGIN',
        model_name='User',
        model_instance_id=user.id,  # Set the model_instance_id to the user's ID
        field_name=None,
        old_value=None,
        new_value=f"{user.username} logged in"
    )
@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Log user logout activity.
    """
    ActivityLog.objects.create(
        user=user if user.is_authenticated else None,  # Log only if the user is authenticated
        action_type='LOGOUT',
        model_name='User',
        model_instance_id=user.id if user.is_authenticated else None,
        field_name=None,
        old_value=None,
        new_value=f"{user.username} logged out" if user.is_authenticated else "Anonymous user logged out"
    )