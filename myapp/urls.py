from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('simulate/', views.simulate, name='simulate'),
    path('leaderboards/', views.leaderboards, name='leaderboards'),
    path('contact/', views.contact, name='contact'),
     path('loginPage', views.loginPage, name='loginPage'),
    path('login', views.login, name='login'),
  path('logout/', LogoutView.as_view(), name='logout'),
 path('profile/', views.profile_view, name='profile'),
 path('logout', views.custom_logout, name='logout'),
]
