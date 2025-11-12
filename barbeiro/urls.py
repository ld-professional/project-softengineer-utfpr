from django.contrib import admin
from django.urls import path,include
from . import views


path('agendamentos/',include('agendamentos.urls')),

path('/dashboard',views.barbeiro_dashboard,name='barbeiro_pagina_inicial_dashboard'),
