from django.contrib import admin
from django.urls import path
from . import views
from .views import EsqueceuSenhaView, NovaSenhaView

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
      path('esqueceu-senha/', EsqueceuSenhaView.as_view(), name='esqueceu_senha'),
    path('nova-senha/<uidb64>/<token>/', NovaSenhaView.as_view(), name='password_reset_confirm'),
    
]
