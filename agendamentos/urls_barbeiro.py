from django.contrib import admin

from django.urls import path,include
from . import views

urlpatterns = [

path('minha-agenda/',views.barbeiro_visualizar_agenda,name='barbeiro_ver_agendamento'),

path('editar-agenda/',views.barbeiro_editar_agenda,name='barbeiro_editar_agendamento'),
]