from django.contrib import admin
from django.urls import path,include
from . import views


path('',views.pagina_inicial_home,name='pagina_inicial'),








