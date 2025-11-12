from django.contrib import admin

from django.urls import path,include
from . import views

urlpatterns = [
path('agendar/',views.cliente_realizar_agendamento,name='cliente_realiza_agendamento'),

]