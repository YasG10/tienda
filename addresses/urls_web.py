from django.urls import path
from . import web_views

app_name = 'addresses'

urlpatterns = [
    path('', web_views.address_list, name='list'),
    path('create/', web_views.address_create, name='create'),
    path('<int:pk>/set-default/', web_views.set_default_address, name='set_default'),
    path('<int:pk>/delete/', web_views.delete_address, name='delete'),
]
