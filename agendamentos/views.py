from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, date
import json
from barbeiro.models import Barbeiro, Horarios_de_trabalho, Excecoes
from servicos.models import Servicos
from clientes.models import Cliente
from .models import Agendamentos


@login_required
def api_ver_horarios(request):

    if request.method != 'GET':
        return JsonResponse({'error': 'Método não permitido.'}, status=405)

    data_busca = request.GET.get('data') 
    servico_id = request.GET.get('servico_id')
        
    if not all([data_busca, servico_id]):
        return JsonResponse(
            {'error': 'Parâmetros de busca insuficientes: data, cliente e serviço são obrigatórios.'}, status=400)
     
    try:
        cliente = Cliente.objects.get(fk_user=request.user)
        cliente_id = cliente.pk
        data_escolhida = datetime.strptime(data_busca, '%Y-%m-%d').date()
        servico = Servicos.objects.get(pk=servico_id)
    
    except (ValueError, Servicos.DoesNotExist, Cliente.DoesNotExist):
        return JsonResponse({'error': 'Dados inválidos ou cliente/serviço não encontrado.'}, status=400)

    duracao_servico_minutos = servico.slot_duracao_servico * 30

    disponibilidade_por_barbeiro = {}

    todos_barbeiros = Barbeiro.objects.all()

    if not todos_barbeiros.exists():
        return JsonResponse({'message': 'Nenhum barbeiro cadastrado.'})

    for barbeiro_obj in todos_barbeiros:
        dia_semana_num = data_escolhida.weekday()

        turnos_base = Horarios_de_trabalho.objects.filter(
            fk_barbeiro=barbeiro_obj,
            dia_semana=dia_semana_num
        )
        if not turnos_base.exists():
            continue
        
        slots_do_dia = []

        for turno in turnos_base:
            
            hora_inicio_turno = datetime.combine(data_escolhida, turno.hora_inicio)
            hora_fim_turno = datetime.combine(data_escolhida, turno.hora_fim)
            
            slot_atual = hora_inicio_turno
            
            while slot_atual < hora_fim_turno:
                slots_do_dia.append(slot_atual)
                slot_atual += timedelta(minutes=30)

        pass



    #verificar ORM de cada objeto barbeiro, horarios e fazer uma lista com todos os horários em que vai ter um barbeiro trabalhando

    #depois de fazer um and entre as 2 listas, é preciso fazer a verificação de exceções, na qual a tabela exceções será verificada e todos os horários inclusos lá serão tirados da lista

    #verificar overlap de serviços

    #reconstruir o json

    #enviar o json

    # Ação: Substituir o 'return 0,'
    return JsonResponse({'message': 'Algoritmo finalizado. Necessita do JSON de saída.'}, status=200)

def agendar_horario(request):

    #converter o json para dictpy

    #criar um objeto na tabela agendamentos e definir fk para os outros modelos

    #retornar o json informando sucesso

    return 0,