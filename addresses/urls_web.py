from django.urls import path
from . import web_views

app_name = 'addresses'

urlpatterns = [
    path('', web_views.address_list, name='list'),
    path('create/', web_views.address_create, name='create'),
]
