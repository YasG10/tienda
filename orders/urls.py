from django.urls import path
from .views import CreateOrderView
from .views import MyOrdersView

urlpatterns = [
    path('create/', CreateOrderView.as_view()),
    path('my/', MyOrdersView.as_view()),

]
