from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta, date
import json

# Importando seus Models
from clientes.models import Cliente
from barbeiro.models import Barbeiro, Horarios_de_trabalho, Excecoes
from servicos.models import Servicos
from .models import Agendamentos



@login_required
@ensure_csrf_cookie
def barbeiro_agendamentos(request):


    if  hasattr(request.user, 'clientao'):
        return redirect('/clientes/dashboard/')

    if not hasattr(request.user, 'barber'):
        return redirect('/account/login')
    


    if request.method == 'GET': 

        lista_agendamentos_do_cliente = Agendamentos.objects.filter(
            fk_barbeiro__fk_user=request.user,
        ).order_by('data_e_horario_inicio')

        contexto = {'agendamentos': lista_agendamentos_do_cliente}

        return render(request, 'agendamentos/barbeiro-meus-agendamentos.html', contexto) 
    
@login_required
@ensure_csrf_cookie
def api_barbeiro_cancelar_meus_agendamentos(request):


        
    if  hasattr(request.user, 'clientao'):
        return redirect('/clientes/dashboard/')

    if not hasattr(request.user, 'barber'):
        return redirect('/account/login')


    try:
        data = json.loads(request.body)
        id_a_cancelar = data.get('id_agendamentos')


        agendamento = get_object_or_404(
            Agendamentos, 
            pk=id_a_cancelar, 
            fk_barbeiro__fk_user=request.user
        )

        agendamento.delete()

        # Retorna sucesso para o JS recarregar a tela
        return JsonResponse({'status': 'success', 'message': 'Agendamento cancelado.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    

from barbeiro.models import Horarios_de_trabalho,Excecoes


def barbeiro_visualizar_agenda(request):
    
    if  hasattr(request.user, 'clientao'):
        return redirect('/clientes/dashboard/')

    if not hasattr(request.user, 'barber'):
        return redirect('/account/login')
    


    if request.method == 'GET': 

        #list_horarios_trab = Horarios_de_trabalho.objects.filter(
        #    fk_barbeiro__fk_user=request.user,
        #).order_by('dia_da_semana','horario_inicio')


        #contexto = {'agendamentos': list_horarios_trab}

        return render(request, 'agendamentos/lista-horarios-trab.html',) 
    
def barbeiro_editar_agenda(request):
    
    if  hasattr(request.user, 'clientao'):
        return redirect('/clientes/dashboard/')

    if not hasattr(request.user, 'barber'):
        return redirect('/account/login')
    


    if request.method == 'GET': 

        lista_agendamentos_do_cliente = Agendamentos.objects.filter(
            fk_barbeiro__fk_user=request.user,
        ).order_by('data_e_horario_inicio')

        contexto = {'agendamentos': lista_agendamentos_do_cliente}

        return render(request, 'agendamentos/excecao.html', contexto) 