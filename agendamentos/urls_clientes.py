from django.urls import path, include
from . import views

urlpatterns = [
    path('escolher_servico/', views.escolher_servico, name='escolher_servico'),
    #path('escolher_barbeiro/', views.escolher_barbeiro, name='escolher_barbeiro'),
    #path('escolher_dia/', views.escolher_dia, name='escolher_dia'),
    
   # path('api/', views.agendamentos_api, name='agendamentos_api'),
]