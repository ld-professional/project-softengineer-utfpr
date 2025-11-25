# agendamentos/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, date, time
import json
from django.views.decorators.http import require_http_methods

# Importação de Modelos
from clientes.models import Cliente
from barbeiro.models import Barbeiro, Horarios_de_trabalho, Excecoes
from servicos.models import Servicos
from .models import Agendamentos 
from core.constantes import ESCOLHER_SERVICO, ESCOLHER_BARBEIRO, ESCOLHER_DIA # Constantes de template

@login_required
@ensure_csrf_cookie
def escolher_servico(request):
    
    if request.method == 'GET':

        lista_servicos= Servicos.objects.all()
        contexto= {'servicos': lista_servicos}

        return render(request,ESCOLHER_SERVICO,contexto)