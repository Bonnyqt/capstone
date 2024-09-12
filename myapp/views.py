from django.shortcuts import render, redirect
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .models import Feedback
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.utils.html import strip_tags
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator



def index(request):
    if request.user.is_authenticated:
        # Fetch the count of feedback for the logged-in user
        feedback_count = Feedback.objects.filter(user=request.user).count()
        # Fetch feedback list (if needed)
        feedback_list = Feedback.objects.filter(user=request.user).order_by('-created_at')
    else:
        feedback_count = 0
        feedback_list = []
    
    # Pass feedback to the template context
    context = {
        'feedback_list': feedback_list,
        'feedback_count': feedback_count,
    }
    return render(request, 'myapp/index.html', context)
    

def about(request):
    if request.user.is_authenticated:
        # Fetch the count of feedback for the logged-in user
        feedback_count = Feedback.objects.filter(user=request.user).count()
        # Fetch feedback list (if needed)
        feedback_list = Feedback.objects.filter(user=request.user).order_by('-created_at')
    else:
        feedback_count = 0
        feedback_list = []
    
    # Pass feedback to the template context
    context = {
        'feedback_list': feedback_list,
        'feedback_count': feedback_count,
    }
    return render(request, 'myapp/about.html', context)

def simulate(request):
    return render(request, 'myapp/simulate.html')

def leaderboards(request):
    if request.user.is_authenticated:
        # Fetch the count of feedback for the logged-in user
        feedback_count = Feedback.objects.filter(user=request.user).count()
        # Fetch feedback list (if needed)
        feedback_list = Feedback.objects.filter(user=request.user).order_by('-created_at')
    else:
        feedback_count = 0
        feedback_list = []
    
    # Pass feedback to the template context
    context = {
        'feedback_list': feedback_list,
        'feedback_count': feedback_count,
    }
    return render(request, 'myapp/leaderboards.html', context)

def contact(request):
    if request.user.is_authenticated:
        # Fetch the count of feedback for the logged-in user
        feedback_count = Feedback.objects.filter(user=request.user).count()
        # Fetch feedback list (if needed)
        feedback_list = Feedback.objects.filter(user=request.user).order_by('-created_at')
    else:
        feedback_count = 0
        feedback_list = []
    
    # Pass feedback to the template context
    context = {
        'feedback_list': feedback_list,
        'feedback_count': feedback_count,
    }
    return render(request, 'myapp/contact.html', context)

def loginPage(request):
    return render(request, 'myapp/login.html')
def profile_view(request):
    if request.user.is_authenticated:
        # Fetch the count of feedback for the logged-in user
        feedback_count = Feedback.objects.filter(user=request.user).count()
        # Fetch feedback list (if needed)
        feedback_list = Feedback.objects.filter(user=request.user).order_by('-created_at')
    else:
        feedback_count = 0
        feedback_list = []
    
    # Pass feedback to the template context
    context = {
        'feedback_list': feedback_list,
        'feedback_count': feedback_count,
    }
    return render(request, 'myapp/profile.html', context)


    

def login(request):
    if request.method == 'POST':
        if 'login' in request.POST:
            # Handle login
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('index')
            else:
                return render(request, 'myapp/login.html', {'error': 'Invalid email or password'})
        
        if 'signup' in request.POST:
            name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email.endswith('@tip.edu.ph'):
            return render(request, 'myapp/login.html', {'error': 'Email must end with @tip.edu.ph'})

        User = get_user_model()
        if User.objects.filter(email=email).exists():
            return render(request, 'myapp/login.html', {'error': 'Email already exists'})

        user = User.objects.create_user(username=email, email=email, password=password)
        user.first_name = name
        user.is_active = False  # Deactivate account until it is confirmed
        user.save()

        # Generate the activation link
        token = account_activation_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        link = f'http://{domain}/activate/{uid}/{token}/'

        # Send email
        subject = 'Activate Your Account'
        message = render_to_string('myapp/activation_email.html', {
            'user': user,
            'domain': domain,
            'link': link,
        })
        plain_message = strip_tags(message)
        send_mail(
    subject,
    plain_message,  # This will be the plain text version
    'marquejonbon@gmail.com',
    [email],
    html_message=message  # This will be the HTML version
)

        return render(request, 'myapp/login.html', {'success': 'Signup successful! Please check your email to activate your account'})
    
  
    

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






def feedback_view(request):
    if request.method == 'POST':
        feedback_text = request.POST.get('feedback')
        user = request.user if request.user.is_authenticated else None
        email = request.POST.get('email') if not user else user.email

        print(f"Feedback: {feedback_text}")
        print(f"Email: {email}")
        print(f"User ID: {user.id if user else 'No user logged in'}")

        # Save the feedback
        Feedback.objects.create(user=user, email=email, feedback=feedback_text)

        # Add a success message
        messages.success(request, 'Your message has been sent successfully!')

        return redirect('contact')  # Replace with your success page URL

    return render(request, 'contact.html')
