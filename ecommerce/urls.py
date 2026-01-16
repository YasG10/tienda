"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core import views as core_views
from core.keepalive import keep_alive
from core.views_about import sobre_nosotros
from core.views_faq import faq
from core.views_admin import admin_dashboard
from orders.views import telegram_webhook
from django.conf import settings
from django.conf.urls.static import static

# Custom error handlers
handler404 = 'core.views.custom_404'

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('panel-admin/', admin_dashboard, name='admin_dashboard'),
    path('api/auth/login/', TokenObtainPairView.as_view()),
    path('api/auth/refresh/', TokenRefreshView.as_view()),
    
    path('api/catalog/', include('catalog.urls')),
    path('api/orders/', include('orders.urls')),

    path('api/users/', include('users.urls')),

    path('', core_views.landing, name='home'),
    path('newsletter/', core_views.newsletter_signup, name='home_newsletter'),
    path('sobre-nosotros/', sobre_nosotros, name='sobre_nosotros'),
    path('preguntas-frecuentes/', faq, name='faq'),
    path('keep-alive/', keep_alive, name='keep_alive'),
    path('telegram/webhook/', telegram_webhook),
    path('', include(('catalog.urls_web', 'catalog'), namespace='catalog')),
    path('accounts/', include(('users.urls_web', 'users'), namespace='users')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('cart/', include(('orders.urls_web', 'orders'), namespace='orders')),
    path('addresses/', include(('addresses.urls_web', 'addresses'), namespace='addresses')),
    path('chat/', include(('chat.urls', 'chat'), namespace='chat')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
