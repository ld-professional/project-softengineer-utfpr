from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('recuperar-senha/', views.esqueceu_senha, name='esqueceu_senha'),
    path('nova-senha/', views.nova_senha, name='nova_senha'),
    
]