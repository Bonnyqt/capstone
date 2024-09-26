from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.views import View
from .models import Feedback
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
import random
import string
from django.db.models import Q

def user_list(request):
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    else:
        users = User.objects.all()

    context = {
        'users': users,
    }
    return render(request, 'myapp/other_profiles.html', context)

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
            return render(request, 'password_reset.html', {'error': 'Email not found'})
    return render(request, 'password_reset.html')

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






def index(request):
    email_count = EmailLog.objects.filter(is_new=True).count()
    
    # Fetch all email logs for display (or apply any other filters you need)
    email_logs = EmailLog.objects.all().order_by('-sent_at')
    blogposts = BlogPost.objects.all()  # Fetch all blog posts

    # Combine context dictionaries
    context = {
        'email_count': email_count,
        'email_logs': email_logs,
        'blogposts': blogposts,  # Include blogposts in the context
    }

    return render(request, 'myapp/index.html', context)


    

def about(request):
    email_count = EmailLog.objects.filter(is_new=True).count()
    
    # Fetch all email logs for display (or apply any other filters you need)
    email_logs = EmailLog.objects.all().order_by('-sent_at')

    # Combine context dictionaries
    context = {
        'email_count': email_count,
        'email_logs': email_logs,
 
    }
    return render(request, 'myapp/about.html', context)

def simulate(request):
    if not request.user.is_authenticated:
        return redirect('index')  # Use your URL name or path for the index page

    return render(request, 'myapp/simulate.html')

def leaderboards(request):
    if not request.user.is_authenticated:
        return redirect('index')  # Use your URL name or path for the index page

    if request.user.is_authenticated:
        # Fetch the count of feedback for the logged-in user
        email_count = EmailLog.objects.filter(is_new=True).count()
        # Fetch feedback list (if needed)
        email_logs = EmailLog.objects.all().order_by('-sent_at')
    
    
    # Pass feedback to the template context
    context = {
        'email_count': email_count,
        'email_logs': email_logs,
     
    }
    
    return render(request, 'myapp/leaderboards.html', context)


    


def contact(request):
    email_count = EmailLog.objects.filter(is_new=True).count()
    
    # Fetch all email logs for display (or apply any other filters you need)
    email_logs = EmailLog.objects.all().order_by('-sent_at')


    # Combine context dictionaries
    context = {
        'email_count': email_count,
        'email_logs': email_logs,
    }
    return render(request, 'myapp/contact.html', context)

def loginPage(request):
    return render(request, 'myapp/login.html')
def terms(request):
    return render(request, 'myapp/terms.html')



    

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
                return render(request, 'myapp/login.html', {'error': 'Invalid email or password'})

        
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






def other_profiles(request):
    query = request.GET.get('q')
    # Get all users excluding superusers by default
    users = User.objects.exclude(is_superuser=True)

    # If a search query is provided, filter the users based on username, first_name, or last_name
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) 
            
        )

    # Email count and logs (remains the same)
    email_count = EmailLog.objects.filter(is_new=True).count()
    email_logs = EmailLog.objects.all().order_by('-sent_at')

    context = {
        'users': users,  # Show all users or filtered users
        'email_count': email_count,
        'email_logs': email_logs,
        'query': query,  # Pass the search query to template
    }
    
    return render(request, 'myapp/other_profiles.html', context)


def profile_details(request):
    users = User.objects.exclude(is_superuser=True)
    email_count = EmailLog.objects.filter(is_new=True).count()
    
    # Fetch all email logs for display (or apply any other filters you need)
    email_logs = EmailLog.objects.all().order_by('-sent_at')

    # Combine context dictionaries
    context = {
        'users': users,
        'email_count': email_count,
        'email_logs': email_logs,
    }
    return render(request, 'myapp/profile_details.html', context)

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('index')  # Use your URL name or path for the index page
    users = User.objects.exclude(is_superuser=True)
    email_count = EmailLog.objects.filter(is_new=True).count()
    
    # Fetch all email logs for display (or apply any other filters you need)
    email_logs = EmailLog.objects.all().order_by('-sent_at')

    # Combine context dictionaries
    context = {
        'users': users,
        'email_count': email_count,
        'email_logs': email_logs,
    }
    return render(request, 'myapp/profile.html',context)

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
    # Check if the user is a superuser
    
    if not request.user.is_superuser:
        return redirect('index')  # Redirect to a forbidden page or wherever you want

    # Fetch users excluding superusers
    users = User.objects.filter(is_superuser=False)

    # Get the count of students (excluding professors and superusers)
    student_count = User.objects.filter(is_superuser=False).exclude(email__endswith='.it@tip.edu.ph').count()

    # Get the count of professors (users with email ending in '.it@tip.edu.ph')
    professor_count = User.objects.filter(is_superuser=False, email__endswith='.it@tip.edu.ph').count()

    # Fetch all feedback
    feedbacks = Feedback.objects.all()  # Fetch all feedback
    feedback_count = feedbacks.count()  # Get the count of feedback

    # Render the data to the template
    return render(request, 'myapp/admin/admin_dashboard.html', {
        'users': users,
        'feedbacks': feedbacks,
        'student_count': student_count,
        'professor_count': professor_count,  # Pass the professor count to the template
        'feedback_count': feedback_count,    # Pass the feedback count to the template
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

def professor_dashboard(request):
    
    # Fetch all users from the database
   
    return render(request, 'myapp/professor/professor_dashboard.html')

def email(request):
    if not request.user.is_superuser:
        return redirect('index') 
    # Exclude superusers from the queryset
    users = User.objects.exclude(is_superuser=True)
    feedbacks = Feedback.objects.all()  # Fetch all feedback
    feedback_count = feedbacks.count()
    context = {
        'users': users,
        'feedbacks': feedbacks,
        'feedback_count': feedback_count,
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

