from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [

path('excluir-servico/',views.excluir_servicos ,name='excluir_servico'),


path('meus-servicos/',views.barbeiros_editar_servicos,name='barbeiro_editar_servicos'),




]







