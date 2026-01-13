from django.urls import path
from . import web_views

app_name = 'users'

urlpatterns = [
    path('register/', web_views.register, name='register'),
    path('profile/', web_views.profile, name='profile'),
]
