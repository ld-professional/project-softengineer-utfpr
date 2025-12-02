from django.contrib import admin

from django.urls import path,include
from . import views_barber

urlpatterns = [

path('', views_barber.barbeiro_agendamentos,name='barbeiro_agendamentos'),

path('cancelar-agendamento/',views_barber.api_barbeiro_cancelar_meus_agendamentos, name='barber_cancelar_agenda'),

path('minha-agenda/',views_barber.barbeiro_visualizar_agenda,name='barbeiro_ver_agendamento'),

path('editar-agenda/',views_barber.barbeiro_editar_agenda,name='barbeiro_editar_agendamento'),

path('excluir-horario/',views_barber.barbeiro_excluir_horario,name='barbeiro_editar_agendamento'),


path('exceccao/',views_barber.barbeiro_exceccao,name='barbeiro_exceccao'),


]