from django.shortcuts import render, redirect
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from .models import Feedback
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'myapp/index.html')

def about(request):
    return render(request, 'myapp/about.html')

def simulate(request):
    return render(request, 'myapp/simulate.html')

def leaderboards(request):
    return render(request, 'myapp/leaderboards.html')

def contact(request):
    return render(request, 'myapp/contact.html')

def loginPage(request):
    return render(request, 'myapp/login.html')
def profile_view(request):
    return render(request, 'myapp/profile.html')


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
        
        elif 'signup' in request.POST:
            # Handle signup
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            # Check if the email ends with @tip.edu.ph
            if not email.endswith('@tip.edu.ph'):
                return render(request, 'myapp/login.html', {'error': 'Email must end with @tip.edu.ph'})
            
            # Check if the email already exists
            if DjangoUser.objects.filter(username=email).exists():
                return render(request, 'myapp/login.html', {'error': 'Email already exists'})
            
            # Create the user
            user = DjangoUser.objects.create_user(username=email, email=email, password=password)
            user.first_name = name
            user.save()
            
            return render(request, 'myapp/login.html', {'success': 'Signup successful! Please login'})
    
    return render(request, 'myapp/login.html')

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
