from django.contrib import admin
from django.urls import path,include
from . import views


path('/agendar',views.cliente_realizar_agendamento,name='cliente_realiza_agendamento'),

path('/minha-agenda',views.barbeiro_visualizar_agenda,name='barbeiro_ver_agendamento'),

path('/editar-agenda',views.barbeiro_editar_agenda,name='barbeiro_editar_agendamento'),
