# accounts/urls.py
from django.urls import path
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('signup/', signup, name='signup'), 
    path('signup/complete/', signup_complete, name='signup_complete'), 
    path('login/', login_view, name='login'),                         
    path('logout/', logout_view, name='logout'),   
    path('check-username/', check_username, name='check_username'),
    path('check-nickname/', check_nickname, name='check_nickname'),
    path('profile/setup/', profile_setup_view, name='profile_setup'),
    path('profile/update/', update_profile, name='update_profile'),                   
]