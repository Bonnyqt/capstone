from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import feedback_view, mark_all_as_read, news, professor_add
from django.conf.urls import handler404
from django.conf import settings
from django.conf.urls.static import static
from .views import user_search
from .views import email
from .views import send_email_view
from .views import terms
from .views import user_list

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
path('profiles-details/', views.profile_details, name='profile_details'),
path('upload_image/', views.upload_image, name='upload_image'),
path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
path('user-accounts/', views.user_accounts, name='user_accounts'),
path('professor-accounts/', views.professor_accounts, name='professor_accounts'),
path('user_feedbacks/', views.user_feedbacks, name='user_feedbacks'),
path('line-graph/', views.get_registration_data, name='get_registration_data'),
path('user-search/', user_search, name='user_search'),
path('professor-dashboard/', views.professor_dashboard, name='professor_dashboard'),
path('professor-announce/', views.professor_announce, name='professor_announce'),
path('email/', email, name='email'),
path('send-email/', send_email_view, name='send_email'),
path('professor-announce-email/', views.professor_announce_email, name='professor_announce_email'),
path('news/', news, name='news'),
path('news/add/', views.add_news, name='add_news'), 
path('terms-and-conditions/', terms, name='terms'),
path('reset_password/', views.reset_password, name='reset_password'),
path('users/', user_list, name='user_list'),
path('professor-add/', professor_add, name='professor_add'),
path('professor-add-defense/', views.professor_add_defense, name='professor_add_defense'),
path('professor-view-challenges/', views.professor_view_challenges, name='professor_view_challenges'),
path('save_canvas_state/', views.save_canvas_state, name='save_canvas_state'),
path('save_canvas_state_defend/', views.save_canvas_state_defend, name='save_canvas_state_defend'),
path('display_canvas/<int:canvas_id>/', views.display_canvas, name='display_canvas'),
path('display_canvas_defend/<int:canvas_id>/', views.display_canvas_defend, name='display_canvas_defend'),
path('remove_challenge/<int:canvas_id>/', views.remove_challenge, name='remove_challenge'),
path('save_score/', views.save_score, name='save_score'),
path('admin-leaderboards/', views.admin_leaderboards, name='admin_leaderboards'),
path('professor-students/', views.professor_students, name='professor_students'),
path('simulate-defend/', views.simulate_defend, name='simulate_defend'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = 'myapp.views.custom_404'