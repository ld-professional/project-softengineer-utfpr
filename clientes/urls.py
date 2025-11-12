from django.contrib import admin
from django.urls import path,include
from . import views


path('agendamentos/',include('agendamentos.urls')),

path('/dashboard',views.cliente_dashboard,name='clientepagina_inicial_dashboard'),
