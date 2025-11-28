from django.contrib import admin

from django.urls import path,include
from . import views_barber

urlpatterns = [

path('minha-agenda/',views_barber.barbeiro_visualizar_agenda,name='barbeiro_ver_agendamento'),

path('editar-agenda/',views_barber.barbeiro_editar_agenda,name='barbeiro_editar_agendamento'),
]