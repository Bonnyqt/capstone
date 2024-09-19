from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import feedback_view, mark_all_as_read
from django.conf.urls import handler404
from .views import user_profiles
from django.conf import settings
from django.conf.urls.static import static
from .views import user_search
from .views import email
from .views import send_email_view

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
   path('profiles-details/', views.profile_details, name='profile_details'),
   path('upload_image/', views.upload_image, name='upload_image'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user-accounts/', views.user_accounts, name='user_accounts'),
     path('professor-accounts/', views.professor_accounts, name='professor_accounts'),
      path('user_feedbacks/', views.user_feedbacks, name='user_feedbacks'),
      path('line-graph/', views.get_registration_data, name='get_registration_data'),
       path('user-search/', user_search, name='user_search'),
       path('professor-dashboard/', views.professor_dashboard, name='professor_dashboard'),
       path('email/', email, name='email'),
        path('send-email/', send_email_view, name='send_email'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = 'myapp.views.custom_404'