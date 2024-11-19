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
from django.conf import settings
from .models import EmailLog
from collections import Counter
import random
import string
from django.db.models import Q
from .models import CanvasState
from django.shortcuts import render, get_object_or_404
from .models import CanvasState
from django.views.decorators.http import require_POST
from .models import Score  # Assuming you have a model to store the score
from django.utils.timezone import now
from django.db import models
@csrf_exempt  # Temporarily exempt CSRF for testing (use proper CSRF handling in production)
@csrf_exempt  # Temporarily exempt CSRF for testing (use proper CSRF handling in production)
def save_score(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            score = data.get('score', 0)
            finished = data.get('finished', False)  # Get the 'finished' status from the request
            category = data.get('category', '')  # Get the category from the request
            correct_submissions = data.get('correct_submissions', 0)  # Get correct submissions count
            incorrect_submissions = data.get('incorrect_submissions', 0)  # Get incorrect submissions count

            # Check if user is authenticated
            if not request.user.is_authenticated:
                return JsonResponse({'status': 'failed', 'message': 'User not authenticated'}, status=401)
            
            # Save the score to the database with user, date_submitted, finished status, category, and submission counts
            user_score = Score.objects.create(
                user=request.user,  # Associate the score with the logged-in user
                score=score,
                date_submitted=now().date(),  # Use current date as submission date
                finished=finished,  # Save the finished status
                category=category,  # Save the category
                correct_submissions=correct_submissions,  # Save the correct submissions count
                incorrect_submissions=incorrect_submissions  # Save the incorrect submissions count
            )
            
            return JsonResponse({
                'status': 'success',
                'score': user_score.score,
                'finished': user_score.finished,
                'category': user_score.category,
                'user': request.user.username,
                'correct_submissions': user_score.correct_submissions,
                'incorrect_submissions': user_score.incorrect_submissions
            })
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'failed', 'message': 'Invalid request method'}, status=400)




def remove_challenge(request, canvas_id):
    # Get the CanvasState object or return 404 if not found
    canvas_state = get_object_or_404(CanvasState, id=canvas_id)
    
    # Delete the canvas state
    canvas_state.delete()

    # Redirect to a page (e.g., a list of challenges or a success message)
    return redirect('professor_view_challenges') 


def display_canvas(request, canvas_id):
    if not request.user.is_authenticated:
        return redirect('index')  # Use your URL name or path for the index page
    # Get the canvas state from the database, return 404 if not found
    canvas_state = get_object_or_404(CanvasState, id=canvas_id)

    # Prepare the canvas state data
    canvas_state_data = {
        'category': canvas_state.category,
        'title': canvas_state.title,
        'nodes': canvas_state.nodes,  # Directly use the Python list from JSONField
        'wires': canvas_state.wires,   # Directly use the Python list from JSONField
    }

    # Render the template with the canvas state data
    return render(request, 'myapp/display_canvas.html', {'canvas_state': canvas_state_data})


def display_canvas_defend(request, canvas_id):
    if not request.user.is_authenticated:
        return redirect('index')  # Use your URL name or path for the index page
    # Get the canvas state from the database, return 404 if not found
    canvas_state_defend = get_object_or_404(CanvasStateDefend, id=canvas_id)
    # Prepare the canvas state data

    canvas_state_defend= {
        'category': canvas_state_defend.category,
        'title': canvas_state_defend.title,
        'nodes': canvas_state_defend.nodes,  # Directly use the Python list from JSONField
        'wires': canvas_state_defend.wires,   # Directly use the Python list from JSONField
    }
    # Render the template with the canvas state data
    return render(request, 'myapp/display_canvas_defend.html', {'canvas_state_defend': canvas_state_defend})
@csrf_exempt
def save_canvas_state(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        category = data.get('category')  # Get category from the request
        difficulty = data.get('difficulty')  # Get difficulty level from the request
        nodes = data.get('nodes')
        wires = data.get('wires')

        # Save the canvas state
        canvas_state = CanvasState.objects.create(
            user=request.user,  # Optionally associate with a user
            title=title,
            category=category,
            difficulty=difficulty,
            nodes=nodes,
            wires=wires
        )

        return JsonResponse({'status': 'success', 'message': 'Canvas state saved successfully!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def user_list(request):
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query
        ))
    else:
        users = User.objects.all()

    context = {
        'users': users,
    }
    return render(request, 'myapp/other_profiles.html', context)


@csrf_exempt
def save_canvas_state_defend(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        category = data.get('category')  # Get category from the request
        difficulty = data.get('difficulty')  # Get difficulty level from the request
        nodes = data.get('nodes')
        wires = data.get('wires')

        # Save the canvas state
        canvas_state = CanvasStateDefend.objects.create(
            user=request.user,  # Optionally associate with a user
            title=title,
            category=category,
            difficulty=difficulty,
            nodes=nodes,
            wires=wires
        )

        return JsonResponse({'status': 'success', 'message': 'Canvas state saved successfully!'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})



def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate a temporary password
            temp_password = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            # Send the temporary password to the user's email
            send_mail(
                'Password Reset',
                f'Your temporary password is: {temp_password}',
                'cyberclash.capstone@gmail.com',  # Replace with your email
                [email],
                fail_silently=False,
            )
            # Update the user's password in the database
            user.set_password(temp_password)
            user.save()
            return redirect('login')
        except User.DoesNotExist:
            return render(request, 'myapp/login.html', {'alert': 'Email not registered! Please register first'})
    return render(request, 'myapp/password_reset.html')

def add_news(request):
    if not request.user.is_superuser:
        return redirect('index') 
    if request.method == 'POST':
        title = request.POST.get('title')
        author = request.POST.get('author')
        date_published = request.POST.get('date_published')
        content = request.POST.get('content')
        image = request.FILES.get('image')

        # Check if all required fields are provided
        if title and author and date_published and content and image:
            # Create and save the new blog post
            try:
                BlogPost.objects.create(
                    title=title,
                    author=author,
                    date_published=date_published,
                    content=content,
                    image=image
                )
                messages.success(request, 'News added successfully.')
                return redirect('news')  # Redirect to news list
            except Exception as e:
                messages.error(request, f'Error adding news: {str(e)}')
        else:
            messages.error(request, 'Please fill out all fields.')

    return render(request, 'myapp/admin/news.html')

def news(request):
    if not request.user.is_superuser:
        return redirect('index') 
    feedbacks = Feedback.objects.all()  # Fetch all feedback
    feedback_count = feedbacks.count() 
    context = {
        'feedback_count':feedback_count,
        'feedbacks': feedbacks,
    }
    return render(request, 'myapp/admin/admin_news.html', context)

def user_search(request):
    if not request.user.is_superuser:
        return redirect('index') 
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(
            first_name__icontains=query
        ) | User.objects.filter(
            email__icontains=query
        ) 
    else:
        users = User.objects.all()

    return render(request, 'myapp/admin/user_accounts.html', {'users': users})

def get_registration_data(request):
    if not request.user.is_superuser:
        return redirect('index') 
    # Query the database for registrations grouped by month
    registration_data = (
        User.objects
        .filter(is_superuser=False) 
        .annotate(month=TruncMonth('date_joined'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )
    
    # Prepare the data for the chart
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    registration_counts = [0] * 12  # Initialize list with 12 zeroes for each month

    for data in registration_data:
        month_number = data['month'].month  # Get the month number (1-12)
        registration_counts[month_number - 1] = data['total']  # Subtract 1 because list is 0-indexed
    
    return JsonResponse({
        'labels': months,
        'data': registration_counts,
    })



def update_profile(request):

    if request.method == "POST":
        # Handle updating the user profile
        user = request.user

        # Update the user's first name
        first_name = request.POST.get('first_name')
        if first_name:
            user.first_name = first_name
            user.save()

        # Handle user profile updates
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            user_profile = UserProfile(user=user)
        
        user_profile.section = request.POST.get('section')
        user_profile.program = request.POST.get('program')
        user_profile.save()

        return redirect('profile_view')  # Redirect to a profile page or another relevant page

    return render(request, 'profile.html', {
        'user': request.user,
        'user_profile': UserProfile.objects.filter(user=request.user).first()
    })


from django.db.models import Sum, F
from .models import EmailLog, BlogPost, Score, User

def index(request):
    if request.user.is_authenticated:
        user = request.user
        # Filter emails for the logged-in user
        email_logs = EmailLog.objects.filter(recipients__icontains=user.email).order_by('-sent_at')
        # Count the number of new emails for the logged-in user
        email_count = EmailLog.objects.filter(recipients__icontains=user.email, is_new=True).count()

        # Calculate the total score for the logged-in user
        total_score = Score.objects.filter(user=user).aggregate(total=Sum('score'))['total'] or 0

        # Get the total score for all users, ordered by score descending
        user_scores = Score.objects.values('user').annotate(total_score=Sum('score')).order_by('-total_score')

        # Calculate the rank of the logged-in user
        rank = next((index + 1 for index, user_score in enumerate(user_scores) if user_score['user'] == user.id), 0)
    else:
        # If the user is not logged in, show no emails and set score to 0
        email_logs = []
        email_count = 0
        total_score = 0
        rank = 0

    blogposts = BlogPost.objects.all()  # Fetch all blog posts

    # Combine context dictionaries
    context = {
        'email_count': email_count,
        'email_logs': email_logs,
        'blogposts': blogposts,  # Include blogposts in the context
        'total_score': total_score,  # Pass total score to the template
        'rank': rank,  # Pass rank to the template
    }

    return render(request, 'myapp/index.html', context)




    

def about(request):
    if request.user.is_authenticated:
        user = request.user
        # Filter emails for the logged-in user
        email_logs = EmailLog.objects.filter(recipients__icontains=user.email).order_by('-sent_at')
        
        # Count the number of new emails for the logged-in user
        email_count = EmailLog.objects.filter(recipients__icontains=user.email, is_new=True).count()
    else:
        # If the user is not logged in, show no emails
        email_logs = []
        email_count = 0

    # Combine context dictionaries
    context = {
        'email_count': email_count,
        'email_logs': email_logs,
 
    }
    return render(request, 'myapp/about.html', context)


def simulate(request):
    if not request.user.is_authenticated:
        return redirect('index')  # Use your URL name or path for the index page

    # Fetch all canvas states (challenges)
    challenges = CanvasState.objects.all()

    # Get the distinct categories from the challenges
    categories = CanvasState.objects.values_list('category', flat=True).distinct()

    context = {
        'challenges': challenges,
        'categories': categories,  # Pass distinct categories
    }
    return render(request, 'myapp/simulate.html', context)

def simulate_defend(request):
    if not request.user.is_authenticated:
        return redirect('index')  # Use your URL name or path for the index page

    # Fetch all canvas states (challenges)
    challenges = CanvasStateDefend.objects.all()

    # Get the distinct categories from the challenges
    categories = CanvasStateDefend.objects.values_list('category', flat=True).distinct()

    context = {
        'challenges': challenges,
        'categories': categories,  # Pass distinct categories
    }
    return render(request, 'myapp/simulate_defend.html', context)

@login_required
def leaderboards(request):
    if not request.user.is_authenticated:
        return redirect('index')  # Redirect if not authenticated

    # Calculate total scores and order users by score in descending order
    user_scores = (
        Score.objects.values('user__id', 'user__first_name', 'user__email')
        .filter(~Q(user__email__endswith='.it@tip.edu.ph'))  # Exclude specific emails
        .annotate(total_score=Sum('score'))  # Sum scores
        .order_by('-total_score')  # Sort by total scores
    )

    # Fetch profile images and other details for users
    user_profiles = UserProfile.objects.filter(user__id__in=[user['user__id'] for user in user_scores])
    profiles_dict = {profile.user.id: profile.profile_image.url for profile in user_profiles}

    # Include profile image URLs, rank, and top category in `user_scores`
    for idx, user_score in enumerate(user_scores, start=1):
        user_score['rank_no'] = idx  # Add rank number
        user_score['profile_image_url'] = profiles_dict.get(user_score['user__id'], '/media/profile_images/default_QBRSs97.jpg')  # Default image if not available
        user_score['username'] = user_score['user__email'].split('@')[0]  # Extract username before '@'

        # Assign ranks
        if user_score['total_score'] == 0:
            user_score['rank'] = "UNRANKED"
        elif 1 <= user_score['total_score'] <= 100:
            user_score['rank'] = "BEGINNER"
        elif 101 <= user_score['total_score'] <= 200:
            user_score['rank'] = "INTERMEDIATE"
        elif 201 <= user_score['total_score'] <= 300:
            user_score['rank'] = "PENETRATION TESTER"
        elif 301 <= user_score['total_score'] <= 400:
            user_score['rank'] = "CERTIFIED ETHICAL HACKER"
        else:
            user_score['rank'] = "Contact Admin"

        # Fetch and calculate the top category answered by the user
        user_canvas_states = CanvasState.objects.filter(user_id=user_score['user__id'])
        if user_canvas_states.exists():
            categories = [state.category for state in user_canvas_states]
            top_category = Counter(categories).most_common(1)  # Get the most common category
            user_score['top_category'] = top_category[0][0] if top_category else "N/A"
        else:
            user_score['top_category'] = "N/A"  # No categories answered

    # Fetch the top 3 users
    top_three = user_scores[:3]

    context = {
        'top_three': top_three,
        'user_scores': user_scores,
    }

    return render(request, 'myapp/leaderboards.html', context)







    


def contact(request):
    if request.user.is_authenticated:
        user = request.user
        # Filter emails for the logged-in user
        email_logs = EmailLog.objects.filter(recipients__icontains=user.email).order_by('-sent_at')
        
        # Count the number of new emails for the logged-in user
        email_count = EmailLog.objects.filter(recipients__icontains=user.email, is_new=True).count()
    else:
        # If the user is not logged in, show no emails
        email_logs = []
        email_count = 0


    # Combine context dictionaries
    context = {
        'email_count': email_count,
        'email_logs': email_logs,
    }
    return render(request, 'myapp/contact.html', context)

def loginPage(request):
    return render(request, 'myapp/login.html',)
def terms(request):
    return render(request, 'myapp/terms.html')

@login_required
def professor_add(request):
    if not request.user.email.endswith('.it@tip.edu.ph'):
        return redirect('index')  

    # Fetch all users or other logic here

    return render(request, 'myapp/professor/professor_add.html')

def professor_add_defense(request):
    return render(request, 'myapp/professor/professor_add_defense.html')
@login_required
def professor_announce(request):
    if not request.user.email.endswith('.it@tip.edu.ph'):
        return redirect('index')  
    # Exclude superusers and users whose email ends with '.it@tip.edu.ph'
    users = User.objects.exclude(Q(is_superuser=True) | Q(email__endswith='.it@tip.edu.ph'))
    # Check if 'recipient' is passed in the query string
    recipient_email = request.GET.get('recipient')
    context = {
        'users': users,

        'selected_recipient': recipient_email,  # Pass the recipient email to the template
    }
    return render(request, 'myapp/professor/professor_announce.html', context)
@login_required
def professor_view_challenges(request):
    if not request.user.email.endswith('.it@tip.edu.ph'):
        return redirect('index')  
    challenges = CanvasState.objects.all()
    canvas_states = CanvasState.objects.all()
    context = {
        'challenges': challenges,
        'canvas_states': canvas_states,
    }
    return render(request, 'myapp/professor/professor_view_challenges.html', context)

    

def login(request):
    if request.method == 'POST':
        if 'login' in request.POST:
        # Handle login
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                auth_login(request, user)
            
            # Check if the user is a superuser (admin)
                if user.is_superuser:
                    return redirect('admin_dashboard')  # Redirect to admin dashboard

            # Check if the email belongs to a professor
                if email.endswith('.it@tip.edu.ph'):
                    return redirect('professor_dashboard')  # Redirect to professor's dashboard

            # Redirect regular users to the index page
                return redirect('index')
            else:
                return render(request, 'myapp/login.html', {'alert': 'Invalid email or password'})

        
        elif 'signup' in request.POST:
    # Handle signup
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            data_privacy_accepted = 'data_privacy' in request.POST

            if not email.endswith('@tip.edu.ph'):
                return render(request, 'myapp/login.html', {'alert': 'Email must end with @tip.edu.ph'})

            if DjangoUser.objects.filter(username=email).exists():
                return render(request, 'myapp/login.html', {'alert': 'Email already exists'})

            user = DjangoUser.objects.create_user(username=email, email=email, password=password)
            user.first_name = name
            user.is_active = False  # Deactivate account until it is confirmed
            user.save()

    # Create or update the UserProfile instance
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.accepted_data_privacy = data_privacy_accepted  # Set acceptance status
            user_profile.save()

    # Generate activation link
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain = '127.0.0.1:8000' if settings.DEBUG else get_current_site(request).domain
            link = f'http://{domain}/activate/{uid}/{token}/'

    # Send email
            subject = 'Activate Your Account'
            message = render_to_string('myapp/activation_email.html', {
                'user': user,
                'domain': domain,
                'link': link,
        })
        plain_message = strip_tags(message)
        send_mail(subject, plain_message, 'your-email@gmail.com', [email], html_message=message)

        return render(request, 'myapp/login.html', {'alert': 'Signup successful! Please check your email to activate your account'})

# Handle GET request or POST without 'login' or 'signup' action
    return render(request, 'myapp/login.html')

  
    

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('login')
    else:
        return render(request, 'myapp/activation_invalid.html')

def custom_logout(request):
    # Log out the user
    logout(request)
    
    # Clear the session data
    request.session.flush()  # This will remove all session data
    
    # Optionally, you can add a message
    
    # Redirect to the login page or homepage
    return redirect('index')



@csrf_exempt
def mark_all_as_read(request):
    if request.method == 'POST':
        EmailLog.objects.filter(is_new=True).update(is_new=False)
        new_email_count = EmailLog.objects.filter(is_new=True).count()
        return JsonResponse({'status': 'success', 'new_email_count': new_email_count})
    return JsonResponse({'status': 'error'}, status=400)

def feedback_view(request):
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback')
        user = request.user if request.user.is_authenticated else None
        email = request.POST.get('email') if not user else user.email
        

        # Save the feedback
        Feedback.objects.create(user=user, email=email, feedback=feedback_text)

        # Add a success message
        return render(request, 'myapp/contact.html', {'alert': 'Feedback sent successfully!'})

        return redirect('contact')  # Replace with your success page URL

    return render(request, 'contact.html')

def custom_404(request, exception=None):
    return render(request, '404.html', status=404)






from django.shortcuts import render
from django.contrib.auth.models import User
from .models import EmailLog
from django.db.models import Q


def other_profiles(request):
    query = request.GET.get('q')
    
    # Get all users, excluding the logged-in user and superusers
    users = User.objects.exclude(id=request.user.id).exclude(is_superuser=True)

    # Exclude users with email ending in .it@tip.edu.ph
    users = users.exclude(email__endswith='.it@tip.edu.ph')

    # If a search query is provided, filter users based on username, first_name, or last_name
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    
    # Annotate users with their total scores
    users = users.annotate(total_score=Sum('score__score')).order_by('-total_score')

    # Add ranks to each user
    for user in users:
        user.total_score = user.total_score or 0  # Handle users with no scores
        if user.total_score == 0:
            user.rank = "UNRANKED"
        elif 1 <= user.total_score <= 100:
            user.rank = "BEGINNER"
        elif 101 <= user.total_score <= 200:
            user.rank = "INTERMEDIATE"
        elif 201 <= user.total_score <= 300:
            user.rank = "PENETRATION TESTER"
        elif 301 <= user.total_score <= 400:
            user.rank = "CERTIFIED ETHICAL HACKER"
        else:
            user.rank = "Contact Admin"

    # Email count and logs for the logged-in user
    if request.user.is_authenticated:
        email_logs = EmailLog.objects.filter(recipients__icontains=request.user.email).order_by('-sent_at')
        email_count = email_logs.filter(is_new=True).count()
    else:
        email_logs = []
        email_count = 0

    context = {
        'users': users,  # Pass the annotated users with scores and ranks
        'email_count': email_count,
        'email_logs': email_logs,
        'query': query,  # Pass the search query to the template
    }

    return render(request, 'myapp/other_profiles.html', context)


def profile_details(request):
    users = User.objects.exclude(is_superuser=True)
    if request.user.is_authenticated:
        user = request.user
        # Filter emails for the logged-in user
        email_logs = EmailLog.objects.filter(recipients__icontains=user.email).order_by('-sent_at')
        
        # Count the number of new emails for the logged-in user
        email_count = EmailLog.objects.filter(recipients__icontains=user.email, is_new=True).count()
    else:
        # If the user is not logged in, show no emails
        email_logs = []
        email_count = 0

    # Combine context dictionaries
    context = {
        'users': users,
        'email_count': email_count,
        'email_logs': email_logs,
    }
    return render(request, 'myapp/profile_details.html', context)

from django.shortcuts import render, redirect
from django.db.models import Sum
from django.contrib.auth.models import User
from .models import Score, EmailLog

@login_required
def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('index')  # Redirect to the index page if the user is not authenticated

    # Filter scores for the logged-in user
    user_score = (
        Score.objects.filter(user=request.user)  # Filter for the logged-in user
        .aggregate(total_score=Sum('score'))  # Calculate total score
    )
    user_score['total_score'] = user_score['total_score'] or 0  # Handle cases with no scores

    # Determine rank based on total score
    total_score = user_score['total_score']
    if total_score == 0:
        rank = "UNRANKED"
    elif 1 <= total_score <= 100:
        rank = "BEGINNER"
    elif 101 <= total_score <= 200:
        rank = "INTERMEDIATE"
    elif 201 <= total_score <= 300:
        rank = "PENETRATION TESTER"
    elif 301 <= total_score <= 400:
        rank = "CERTIFIED ETHICAL HACKER"
    else:
        rank = "Contact Admin"

    # Get email logs for the logged-in user
    email_logs = EmailLog.objects.filter(recipients__icontains=request.user.email).order_by('-sent_at')

    # Count new emails for the logged-in user
    email_count = email_logs.filter(is_new=True).count()

    # Aggregate submission counts by category for the logged-in user
    category_submission_counts = Score.objects.filter(user=request.user) \
        .values('category') \
        .annotate(submission_count=Count('category')) \
        .order_by('category')

    # Prepare data for the progress bars
    categories = [entry['category'] for entry in category_submission_counts]
    submission_counts = [entry['submission_count'] for entry in category_submission_counts]
    # Aggregate submission counts by category for the logged-in user
    category_submission_counts = Score.objects.filter(user=request.user) \
        .values('category') \
        .annotate(
            total_correct=Sum('correct_submissions'),
            total_incorrect=Sum('incorrect_submissions')
        )

    # Prepare data for performance, including dynamic percentages
    performance_data = []
    for entry in category_submission_counts:
        total = (entry['total_correct'] or 0) + (entry['total_incorrect'] or 0)
        performance_data.append({
            'category': entry['category'],
            'correct_ratio': round((entry['total_correct'] or 0) / total * 100, 2) if total > 0 else 0,
            'incorrect_ratio': round((entry['total_incorrect'] or 0) / total * 100, 2) if total > 0 else 0,
        })
    context = {
        'email_count': email_count,
        'email_logs': email_logs,
        'user_score': user_score,
        'rank': rank,
        'categories': categories,
        'submission_counts': submission_counts,
        'performance_data': performance_data,

    }

    return render(request, 'myapp/profile.html', context)




@login_required
def upload_image(request):
    if request.method == 'POST' and 'profile_image' in request.FILES:
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.profile_image = request.FILES['profile_image']
        user_profile.save()
        return redirect('profile_view')
    return redirect('profile_view')
    
@login_required
def update_profile(request):
    # Ensure that UserProfile exists for the current user
    if not hasattr(request.user, 'userprofile'):
        UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        # Process the form data
        form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            # Update user first name separately
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.save()
            return redirect('profile_view')
    else:
        form = UserProfileForm(instance=request.user.userprofile)

    return render(request, 'myapp/profile.html', {'form': form})




@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('index')  # Redirect to a forbidden page or wherever you want

    # Fetch users excluding superusers
    users = User.objects.filter(is_superuser=False)

    # Get the count of students (excluding professors and superusers)
    student_count = User.objects.filter(is_superuser=False).exclude(email__endswith='.it@tip.edu.ph').count()
    student_status = User.objects.filter(userprofile__is_online=True, is_superuser=False).count()
    # Get the count of professors (users with email ending in '.it@tip.edu.ph')
    professor_count = User.objects.filter(is_superuser=False, email__endswith='.it@tip.edu.ph').count()

    # Aggregate submissions by category for all time
    category_submission_counts = Score.objects.values('category') \
        .annotate(submission_count=Count('category')) \
        .order_by('category')

    # Convert data into a format for the pie chart
    categories = [entry['category'] for entry in category_submission_counts]
    submission_counts = [entry['submission_count'] for entry in category_submission_counts]

    # Aggregate total scores per user
    user_scores = Score.objects.values('user') \
        .annotate(total_score=Sum('score')) \
        .order_by('-total_score')  # Order by total_score in descending order

    # Prepare data for the bar chart
    users_names = [User.objects.get(id=entry['user']).username for entry in user_scores]
    total_scores = [entry['total_score'] for entry in user_scores]

    # Fetch all feedback and challenges
    feedbacks = Feedback.objects.all()
    feedback_count = feedbacks.count()
    challenges = CanvasState.objects.all()
    challenges_count = challenges.count()

    # Render the data to the template
    return render(request, 'myapp/admin/admin_dashboard.html', {
        'users': users,
        'challenges_count': challenges_count,
        'student_status': student_status,
        'feedbacks': feedbacks,
        'student_count': student_count,
        'professor_count': professor_count,
        'feedback_count': feedback_count,
        'categories': categories,
        'submission_counts': submission_counts,
        'users_names': users_names,
        'total_scores': total_scores,
    })

@login_required
def admin_leaderboards(request):
    # Check if the user is a superuser
    if not request.user.is_superuser:
        return redirect('index')  # Redirect to a forbidden page or wherever you want

    # Fetch users excluding those with email ending in '.it@tip.edu.ph'
    users = User.objects.filter(is_superuser=False).exclude(email__endswith='.it@tip.edu.ph')
    # Calculate total scores for users and order by score in descending order (highest score first)
    user_scores = (
        Score.objects.values('user__id', 'user__first_name', 'user__email')
        .annotate(total_score=Sum('score'))  # Sum the scores for each user
        .order_by('-total_score')  # Sort by total score in descending order
    )

    # Assign ranks based on score order
    for idx, user_score in enumerate(user_scores, start=1):
        user_score['rank_no'] = idx  # Rank number, starting from 1
        if user_score['total_score'] == 0:
            user_score['rank'] = "UNRANKED"
        elif 1 <= user_score['total_score'] <= 100:
            user_score['rank'] = "BEGINNER"
        elif 101 <= user_score['total_score'] <= 200:
            user_score['rank'] = "INTERMEDIATE"
        elif 201 <= user_score['total_score'] <= 300:
            user_score['rank'] = "PENETRATION TESTER"
        elif 301 <= user_score['total_score'] <= 400:
            user_score['rank'] = "CERTIFIED ETHICAL HACKER"
        else:
            user_score['rank'] = "Contact Admin"

    if request.method == 'POST':
        for user in users:
            first_name = request.POST.get(f'first_name_{user.id}')
            email = request.POST.get(f'email_{user.id}')
            user.first_name = first_name
            user.email = email
            user.save()  # Save the updated user

        # Redirect to the same page to avoid resubmission
        return redirect('user_accounts')

    feedbacks = Feedback.objects.all()  # Fetch all feedback
    feedback_count = feedbacks.count()  # Get the count of feedback

    # Render the data to the template
    return render(request, 'myapp/admin/admin_leaderboards.html', {
        'user_scores': user_scores,
        'feedback_count': feedback_count,
        'feedbacks': feedbacks,
    })

@login_required
def professor_students(request):


    # Fetch users excluding those with email ending in '.it@tip.edu.ph'
    users = User.objects.filter(is_superuser=False).exclude(email__endswith='.it@tip.edu.ph')
    # Calculate total scores for users and order by score in descending order (highest score first)
    user_scores = (
        Score.objects.values('user__id', 'user__first_name', 'user__email')
        .annotate(total_score=Sum('score'))  # Sum the scores for each user
        .order_by('-total_score')  # Sort by total score in descending order
    )

    # Assign ranks based on score order
    for idx, user_score in enumerate(user_scores, start=1):
        user_score['rank_no'] = idx  # Rank number, starting from 1
        if user_score['total_score'] == 0:
            user_score['rank'] = "UNRANKED"
        elif 1 <= user_score['total_score'] <= 100:
            user_score['rank'] = "BEGINNER"
        elif 101 <= user_score['total_score'] <= 200:
            user_score['rank'] = "INTERMEDIATE"
        elif 201 <= user_score['total_score'] <= 300:
            user_score['rank'] = "PENETRATION TESTER"
        elif 301 <= user_score['total_score'] <= 400:
            user_score['rank'] = "CERTIFIED ETHICAL HACKER"
        else:
            user_score['rank'] = "Contact Admin"

    if request.method == 'POST':
        for user in users:
            first_name = request.POST.get(f'first_name_{user.id}')
            email = request.POST.get(f'email_{user.id}')
            user.first_name = first_name
            user.email = email
            user.save()  # Save the updated user

        # Redirect to the same page to avoid resubmission
        return redirect('user_accounts')

   
    # Render the data to the template
    return render(request, 'myapp/professor/professor_students.html', {
        'user_scores': user_scores,
    
    })


@login_required
def user_accounts(request):
    # Check if the user is a superuser
    if not request.user.is_superuser:
        return redirect('index')  # Redirect to a forbidden page or wherever you want

    # Fetch users excluding those with email ending in '.it@tip.edu.ph'
    users = User.objects.filter(is_superuser=False).exclude(email__endswith='.it@tip.edu.ph')
    
    if request.method == 'POST':
        for user in users:
            first_name = request.POST.get(f'first_name_{user.id}')
            email = request.POST.get(f'email_{user.id}')
            user.first_name = first_name
            user.email = email
            user.save()  # Save the updated user
            
        # Redirect to the same page to avoid resubmission
        return redirect('user_accounts')
    feedbacks = Feedback.objects.all()  # Fetch all feedback
    feedback_count = feedbacks.count()  # Get the count of feedback
    # Render the data to the template
    return render(request, 'myapp/admin/user_accounts.html', {
        'users': users,
        'feedback_count':feedback_count,
        'feedbacks': feedbacks,
    })

@login_required
def professor_accounts(request):
    # Check if the user is a superuser
    if not request.user.is_superuser:
        return redirect('index')  # Redirect to a forbidden page or wherever you want

    # Fetch users who are not superusers and include those with email ending in '.it@tip.edu.ph'
    users = User.objects.filter(is_superuser=False).filter(
        email__endswith='.it@tip.edu.ph'
    ).union(
        User.objects.filter(is_superuser=False).exclude(email__endswith='@tip.edu.ph')
    )

    if request.method == 'POST':
        for user in users:
            first_name = request.POST.get(f'first_name_{user.id}')
            email = request.POST.get(f'email_{user.id}')
            user.first_name = first_name
            user.email = email
            user.save()  # Save the updated user

        # Redirect to the same page to avoid resubmission
        return redirect('professor_accounts')
    feedbacks = Feedback.objects.all()  # Fetch all feedback
    feedback_count = feedbacks.count()  # Get the count of feedback
    # Render the data to the template
    return render(request, 'myapp/admin/professor_accounts.html', {
        'users': users,
        'feedback_count':feedback_count,
        'feedbacks': feedbacks,
    })


@login_required
def user_feedbacks(request):
    # Check if the user is a superuser
    if not request.user.is_superuser:
        return redirect('index')  # Redirect to a forbidden page or wherever you want

    # Fetch users and feedback from the database
    users = User.objects.all()  # Fetch all users
    feedbacks = Feedback.objects.all()  # Fetch all feedback
    feedback_count = feedbacks.count()
    # Render the data to the template
    return render(request, 'myapp/admin/user_feedbacks.html', {
        'users': users,
        'feedbacks': feedbacks,
        'feedback_count': feedback_count,
    })

@login_required
def professor_dashboard(request):
    # Check if the logged-in user's email ends with '.it@tip.edu.ph'
    if not request.user.email.endswith('.it@tip.edu.ph'):
        # Redirect to an unauthorized page or home page
        return redirect('index')  # Replace 'unauthorized' with the name of your unauthorized page URL

    # Fetch all users or other logic here
    return render(request, 'myapp/professor/professor_dashboard.html')

def email(request):
    if not request.user.is_superuser:
        return redirect('index') 
    
    # Exclude superusers from the queryset
    users = User.objects.exclude(is_superuser=True)
    feedbacks = Feedback.objects.all()  # Fetch all feedback
    
    # Check if 'recipient' is passed in the query string
    recipient_email = request.GET.get('recipient')
    
    context = {
        'users': users,
        'feedbacks': feedbacks,
        'feedback_count': feedbacks.count(),
        'selected_recipient': recipient_email,  # Pass the recipient email to the template
    }
    
    return render(request, 'myapp/admin/email.html', context)



def send_email_view(request):
    if not request.user.is_superuser:
        return redirect('index') 
    if request.method == 'POST':
        recipients = request.POST.getlist('recipients')
        subject = request.POST.get('subject')
        body = request.POST.get('body')

        # Prepare email data
        if 'all' in recipients:
            # If 'all' is selected, get all user emails
            recipient_emails = [user.email for user in User.objects.all()]
        else:
            recipient_emails = recipients

        # Send email
        try:
            send_mail(
                subject,
                body,
                settings.EMAIL_HOST_USER,
                recipient_emails,
                fail_silently=False,
            )

            # Save email details to the database
            EmailLog.objects.create(
                recipients=', '.join(recipient_emails),
                subject=subject,
                body=body,
                sent_by=request.user if request.user.is_authenticated else None
            )

            messages.success(request, 'Email sent successfully!')
        except Exception as e:
            messages.error(request, f'Error sending email: {e}')
        
        return redirect('email')  # Redirect after successful send

    # Render your form template if not a POST request
    return render(request, 'myapp/admin/email.html')


def professor_announce_email(request):
    if request.method == 'POST':
        recipients = request.POST.getlist('recipients')
        subject = request.POST.get('subject')
        body = request.POST.get('body')

        # Prepare email data
        if 'all' in recipients:
            # If 'all' is selected, get all user emails
            recipient_emails = [user.email for user in User.objects.all()]
        else:
            recipient_emails = recipients

        # Send email
        try:
            send_mail(
                subject,
                body,
                settings.EMAIL_HOST_USER,
                recipient_emails,
                fail_silently=False,
            )

            # Save email details to the database
            EmailLog.objects.create(
                recipients=', '.join(recipient_emails),
                subject=subject,
                body=body,
                sent_by=request.user if request.user.is_authenticated else None
            )

            messages.success(request, 'Email sent successfully!')
        except Exception as e:
            messages.error(request, f'Error sending email: {e}')
        
        return redirect('professor_announce')  # Redirect after successful send

    # Render your form template if not a POST request
    return render(request, 'myapp/professor/professor_announce.html')