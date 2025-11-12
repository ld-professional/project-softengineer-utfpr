from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
path('agendamentos/',include('agendamentos.urls_clientes')),

path('dashboard/',views.cliente_dashboard,name='clientepagina_inicial_dashboard'),
]