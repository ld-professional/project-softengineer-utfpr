# agendamentos/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
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

# =======================================================
# 1. FUNÇÕES DE RENDERIZAÇÃO (SSR)
# =======================================================

@login_required
@require_http_methods(["GET"])
def escolher_servico(request):
    # Rota 1: Busca e exibe todos os serviços disponíveis
    servicos = Servicos.objects.all().order_by('preco_servico')
    contexto = {
        'servicos': servicos
    }
    return render(request, ESCOLHER_SERVICO, contexto)


@login_required
@require_http_methods(["GET"])
def escolher_barbeiro(request):
    # Rota 2: Recebe servico_id e exibe barbeiros
    servico_id = request.GET.get('servico_id')
    
    if not servico_id:
        return redirect('escolher_servico')
    
    barbeiros_disponiveis = Barbeiro.objects.all().select_related('fk_user')

    contexto = {
        'barbeiros': barbeiros_disponiveis,
        'servico_id': servico_id
    }
    return render(request, ESCOLHER_BARBEIRO, contexto)


@login_required
@require_http_methods(["GET"])
def escolher_dia(request):
    # Rota 3: Recebe servico_id e barbeiro_id e exibe o calendário
    servico_id = request.GET.get('servico_id')
    barbeiro_id = request.GET.get('barbeiro_id')
    
    if not servico_id or not barbeiro_id:
        return redirect('escolher_servico')
        
    try:
        servico = Servicos.objects.get(pk=servico_id)
        barbeiro = Barbeiro.objects.get(pk=barbeiro_id)
        
    except (Servicos.DoesNotExist, Barbeiro.DoesNotExist):
        return JsonResponse(
            {'error': 'Serviço ou Barbeiro não encontrado. IDs inválidos.'},
            status=404)

    contexto = {
        'servico': servico,
        'barbeiro': barbeiro,
        'servico_id': servico_id,
        'barbeiro_id': barbeiro_id,
    }
    
    return render(request, ESCOLHER_DIA, contexto)

# =======================================================
# 2. VIEW UNIFICADA DE API (GET: Consulta / POST: Criação)
# =======================================================

@login_required
def agendamentos_api(request):
    
    if request.method not in ['GET', 'POST']:
        return JsonResponse({'error': 'Método não permitido.'}, status=405)

    # -----------------------------------------------------------
    # LÓGICA DE CRIAÇÃO (POST)
    # -----------------------------------------------------------
    if request.method == 'POST':
        try:
            data_json = json.loads(request.body)
            data_hora_inicio_str = data_json.get('data_e_horario_inicio')
            barbeiro_id = data_json.get('barbeiro_id')
            servico_id = data_json.get('servico_id')
            
            if not all([data_hora_inicio_str, barbeiro_id, servico_id]):
                return JsonResponse({'error': 'Todos os dados de agendamento são obrigatórios.'}, status=400)
            
            data_hora_inicio = datetime.strptime(data_hora_inicio_str, '%Y-%m-%d %H:%M')
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido.'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Formato de data/hora inválido. Use YYYY-MM-DD HH:MM.'}, status=400)

        try:
            with transaction.atomic():
                cliente = Cliente.objects.get(fk_user=request.user)
                barbeiro = Barbeiro.objects.get(pk=barbeiro_id)
                servico = Servicos.objects.get(pk=servico_id)
                
                # A validação de sobreposição acontece automaticamente no Agendamentos.clean()
                Agendamentos.objects.create(
                    fk_cliente=cliente,
                    fk_barbeiro=barbeiro,
                    fk_servicos=servico,
                    data_e_horario_inicio=data_hora_inicio,
                )
            
            return JsonResponse({'success': True, 'message': 'Agendamento confirmado com sucesso!'}, status=201)

        except ValidationError as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=409) 
