from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
path('',views.pagina_inicial_home,name='pagina_inicial'),
]







