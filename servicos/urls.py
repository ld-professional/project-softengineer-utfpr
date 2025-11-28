from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
path('meus-servicos/',views.barbeiros_visualizar_servicos,name='barbeiro_visualizar_servicos'),

path('excluir-servico/',views.excluir_servicos ,name='excluir_servico'),


#path('editar-servicos/',views.barbeiros_editar_servicos,name='barbeiro_editar_servicos'),




]







