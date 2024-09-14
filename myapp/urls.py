from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import feedback_view, mark_all_as_read
from django.conf.urls import handler404
from .views import user_profiles
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('simulate/', views.simulate, name='simulate'),
    path('leaderboards/', views.leaderboards, name='leaderboards'),
    path('contact/', views.contact, name='contact'),
     path('loginPage', views.loginPage, name='loginPage'),
    path('login', views.login, name='login'),
  path('logout/', LogoutView.as_view(), name='logout'),
 path('profile_view/', views.profile_view, name='profile_view'),
 path('logout', views.custom_logout, name='logout'),
 path('feedback/', feedback_view, name='feedback_view'),
 path('activate/<uidb64>/<token>/', views.activate, name='activate'),
  path('mark-all-as-read/', mark_all_as_read, name='mark_all_as_read'),
   path('profile/', views.update_profile, name='update_profile'),
   path('other-profiles/', views.other_profiles, name='other_profiles'),
   path('profiles/', user_profiles, name='user_profiles'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = 'myapp.views.custom_404'