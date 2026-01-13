from django.urls import path
from .views import CategoryListView, ProductListView
from .views_ofertas import ofertas





urlpatterns = [
    path('categories/', CategoryListView.as_view()),
    path('products/', ProductListView.as_view()),
    path('ofertas/', ofertas, name='ofertas'),
    
]
