from django.shortcuts import render, redirect
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.contrib import messages


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
    messages.success(request, "You have been logged out successfully.")
    
    # Redirect to the login page or homepage
    return redirect('loginPage')