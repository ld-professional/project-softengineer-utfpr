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
    


@login_required
@ensure_csrf_cookie
def escolher_barbeiro(request):
    # É aqui que a mágica acontece.
    # O request.GET é um dicionário com tudo que veio na URL depois do ?
    id_do_servico = request.GET.get('id_servico')
    
    # Validação simples: se o usuário tentar entrar direto na URL sem escolher serviço
    if not id_do_servico:
        return redirect('escolher_servico') # Manda ele voltar pra tela anterior


    lista_barbeiros= Barbeiro.objects.all()

    contexto={'barbeiros': lista_barbeiros}

    contexto['id_servico_escolhido']=id_do_servico
    # Agora você tem o ID (ex: "1", "5") e pode buscar no banco
    # Exemplo: trazer só barbeiros que fazem esse serviço
    # servico = Servico.objects.get(id=id_do_servico)
    
    return render(request,ESCOLHER_BARBEIRO, contexto)



def escolher_dia(request):

    if request.method == 'GET':
        return render(request,ESCOLHER_DIA)

