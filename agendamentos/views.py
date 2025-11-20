from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, date
import json

from clientes.models import Cliente
from barbeiro.models import Barbeiro, Horarios_de_trabalho, Excecoes
from servicos.models import Servicos
from .models import Agendamentos 

@login_required
def agendar_horario(request):
    
    #método deve ser post
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido.'}, status=405)
    
    #decodificamos o json em dictpy
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
        return JsonResponse({'error': 'Formato de data/hora inválido.'}, status=400)

    #criação do agendamento
    try:
        #garantimos a atomicidade
        with transaction.atomic():
            cliente = Cliente.objects.get(fk_user=request.user)
            barbeiro = Barbeiro.objects.get(pk=barbeiro_id)
            servico = Servicos.objects.get(pk=servico_id)
            
            Agendamentos.objects.create(
                fk_cliente=cliente,
                fk_barbeiro=barbeiro,
                fk_servicos=servico,
                data_e_horario_inicio=data_hora_inicio,
            )
        
        return JsonResponse({'success': True, 'message': 'Agendamento confirmado com sucesso!'}, status=201)

    except Exception as e:
        # Erro de BD ou erro de Conflito (levantado pelo clean() do Agendamentos)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)









@login_required
def api_ver_horarios(request):

    #verificamos se é .get, pois é o método que vamos usar (consulta)
    if request.method != 'GET':
        return JsonResponse({'error': 'Método não permitido.'}, status=405)

    #extraímos as duas variáveis de request e verificamos se elas vieram
    data_str = request.GET.get('data') 
    servico_id = request.GET.get('servico_id')
    
    if not all([data_str, servico_id]):
        return JsonResponse(
            {'error': 'Data e Serviço são obrigatórios.'}, status=400)
     
    #extraímos o cliente_id de forma segura por meio da fk do user
    try:
        cliente = Cliente.objects.get(fk_user=request.user)
        cliente_id = cliente.pk
        #extraímos a data em forma de objeto date puro através da string que fizemos antes, especificada no formato abaixo
        data_escolhida = datetime.strptime(data_str, '%Y-%m-%d').date()
        servico = Servicos.objects.get(pk=servico_id)
    
    except (ValueError, Servicos.DoesNotExist, Cliente.DoesNotExist):
        return JsonResponse({'error': 'Dados inválidos ou cliente/serviço não encontrado.'}, status=400)

    #definimos o tempo total do serviço, em minutos, e criamos a lista dos slots disponíveis para cada barbeiro
    duracao_servico_minutos = servico.slot_duracao_servico * 30
    disponibilidade_por_barbeiro = {}
    
    #consultamos todos os barbeiros registrados
    todos_barbeiros = Barbeiro.objects.all()

    #verificamos se há ao menos um barbeiro existente
    if not todos_barbeiros.exists():
        return JsonResponse({'message': 'Nenhum barbeiro cadastrado.'})
    
    #usamos a função weekday para receber um inteiro que representa o dia da semana da data_escolhida
    dia_semana = data_escolhida.weekday() # 0 = Segunda, 6 = Domingo

    #loop principal: iteramos em cada barbeiro ativo
    for barbeiro_obj in todos_barbeiros:
        
        #objeto horarios do barbeiro e do dia da semana específicos. Agora temos o início e o fim do turno do barbeiro da iteração.
        turnos_base = Horarios_de_trabalho.objects.filter(
            fk_barbeiro=barbeiro_obj,
            dia_semana=dia_semana
        )
        if not turnos_base.exists():
            continue 
        
        #criação de todos os inícios de horários do/dos turnos do barbeiro no dia em questão.
        slots_do_dia = []
        for turno in turnos_base:
            hora_inicio_turno = datetime.combine(data_escolhida, turno.hora_inicio)
            hora_fim_turno = datetime.combine(data_escolhida, turno.hora_fim)
            slot_atual = hora_inicio_turno
            
            # Geração de 30 em 30 minutos (considerando a duração do serviço)
            while slot_atual + timedelta(minutes=duracao_servico_minutos) <= hora_fim_turno:
                slots_do_dia.append(slot_atual)
                slot_atual += timedelta(minutes=30)

        #ao final da iteração, temos todos os slots (inícios de 30 min ex:8:00-8:30 é o slot 8:00) do dia para o barbeiro.

        #aqui definimos uma estrutura de dados do python set(), que funciona como um aglomerado de dados desordenados. Utilizei pois é mais eficiente em realizar operações, já que vou subtrair de slots_do_dia daqui a pouco e fazer isso entre 2 listas é O(n) e não O(1), como é o caso de set.
        slots_bloqueados_por_excecao = set()
        slots_bloqueados_por_agendamento = set()
        
        # --- A. Exceções (Consulta e Geração do Set de Bloqueio) ---
        excecoes_db = Excecoes.objects.filter(
            fk_barbeiro=barbeiro_obj,
            data_inicio__date=data_escolhida#usamos o lookup __date para dizer ao Django que queremos o filtro apenas com a parte da data e não do horário.
        )
        for excecao in excecoes_db:
            inicio_bloqueio = excecao.data_inicio
            fim_bloqueio = excecao.data_fim
            slot_atual_bloqueio = inicio_bloqueio
            while slot_atual_bloqueio < fim_bloqueio:
                slots_bloqueados_por_excecao.add(slot_atual_bloqueio)
                slot_atual_bloqueio += timedelta(minutes=30)


        #fazemos a mesma filtragem para agendamentos
        agendamentos_ocupados = Agendamentos.objects.filter(
            fk_barbeiro=barbeiro_obj,
            data_e_horario_inicio__date=data_escolhida
        )
        for agendamento in agendamentos_ocupados:
            inicio_ocupado = agendamento.data_e_horario_inicio
            fim_ocupado = agendamento.data_e_horario_fim
            slot_bloqueio = inicio_ocupado
            while slot_bloqueio < fim_ocupado:
                slots_bloqueados_por_agendamento.add(slot_bloqueio)
                slot_bloqueio += timedelta(minutes=30)
                
        #checamos se há algum agendamento do próprio cliente para o barbeiro da iteração no dia específico
        meus_agendamentos_db = Agendamentos.objects.filter(
            fk_cliente=cliente_id,
            fk_barbeiro=barbeiro_obj,
            data_e_horario_inicio__date=data_escolhida
        )
        meus_slots_formatados = [
            agendamento.data_e_horario_inicio.strftime('%H:%M')
            for agendamento in meus_agendamentos_db
            ]

        #somamos todos os slots indisponíveis
        todos_slots_bloqueados = slots_bloqueados_por_excecao | slots_bloqueados_por_agendamento

        #subtraímos os slots totais dos slots bloqueados
        slots_finais_datetime = [
            slot for slot in slots_do_dia 
            if slot not in todos_slots_bloqueados
        ]

        #formatamos para hora:minutos
        slots_disponiveis_formatados = [
            slot.strftime('%H:%M') for slot in slots_finais_datetime
        ]

        #armazenamos o resultado de toda a busca por esse barbeiro no formato abaixo, já abrindo uma pré-formatação para o Json. No retorno, cada barbeiro possui esses 3 campos abaixo.
        disponibilidade_por_barbeiro[barbeiro_obj.fk_user.username] = {
            'disponiveis': slots_disponiveis_formatados,
            'meus_agendamentos': meus_slots_formatados, 
            'barbeiro_id': barbeiro_obj.pk,
        }

    #retorno final
    return JsonResponse({'disponibilidade': disponibilidade_por_barbeiro}, status=200)
