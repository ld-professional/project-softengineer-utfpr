from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.db import transaction
from django.core.exceptions import ValidationError
import json
from django.views.decorators.http import require_http_methods


from clientes.models import Cliente
from barbeiro.models import Barbeiro, Horarios_de_trabalho, Excecoes
from servicos.models import Servicos
from .models import Agendamentos 
from core.constantes import ESCOLHER_SERVICO, ESCOLHER_BARBEIRO, ESCOLHER_DIA 
from datetime import datetime, timedelta



@login_required
@ensure_csrf_cookie
def escolher_servico(request):

    if request.method == 'GET':

        lista_servicos = Servicos.objects.all()

        contexto = {'servicos': lista_servicos}

        return render(request, ESCOLHER_SERVICO, contexto)
    



@login_required
@ensure_csrf_cookie
def escolher_barbeiro(request):

    id_do_servico = request.GET.get('id_servico')

    if not id_do_servico:

        return redirect('escolher_servico')
    
    lista_barbeiros = Barbeiro.objects.all()

    contexto = {'barbeiros': lista_barbeiros}

    contexto['id_servico_escolhido'] = id_do_servico

    return render(request, ESCOLHER_BARBEIRO, contexto)




@login_required
@ensure_csrf_cookie
def escolher_dia(request):

    if request.method == 'GET':

        id_do_serv = request.GET.get('id_servico')

        id_do_barb = request.GET.get('id_barbeiro')
        
        if not id_do_serv or not id_do_barb:
            return redirect('escolher_servico') 

        contexto = {
            'barbeiro_id': id_do_barb,
            'servico_id': id_do_serv
        }

        return render(request, ESCOLHER_DIA, contexto)



@login_required
def agendamentorealizado(request):

    if request.method == 'GET':
        return render(request,'agendamentos/agenda-realizado.html')


@login_required
def buscar_horarios_api(request):

    data_texto = request.GET.get('data')
    id_barbeiro = request.GET.get('id_barbeiro')
    id_servico = request.GET.get('id_servico')

    if not data_texto or not id_barbeiro or not id_servico:
        return JsonResponse({'erro': 'Faltam dados.'}, status=400)
    
    try:
        data_desejavel_agendar = datetime.strptime(data_texto, '%Y-%m-%d').date()
        dia_da_semana_numero = data_desejavel_agendar.weekday()
        
        turnos_de_trabalho = Horarios_de_trabalho.objects.filter(
            fk_barbeiro_id=id_barbeiro,
            dia_semana=dia_da_semana_numero
        )

        if not turnos_de_trabalho.exists():
            return JsonResponse({'horarios': [], 'mensagem': 'Barbeiro não trabalha neste dia.'})

        agendamentos_do_dia = Agendamentos.objects.filter(fk_barbeiro_id=id_barbeiro, data_e_horario_inicio__date=data_desejavel_agendar)
        excecoes_do_dia = Excecoes.objects.filter(fk_barbeiro_id=id_barbeiro, data_inicio__date__lte=data_desejavel_agendar, data_fim__date__gte=data_desejavel_agendar)

        servico = Servicos.objects.get(pk=id_servico)
        duracao_em_minutos = servico.slot_duracao_servico * 30 
        lista_horarios_livres = []

        for turno in turnos_de_trabalho:
            inicio_do_slot = datetime.combine(data_desejavel_agendar, turno.hora_inicio)
            fim_do_expediente = datetime.combine(data_desejavel_agendar, turno.hora_fim)

            while inicio_do_slot + timedelta(minutes=duracao_em_minutos) <= fim_do_expediente:
                fim_do_slot = inicio_do_slot + timedelta(minutes=duracao_em_minutos)
                esta_livre = True

                for agendamento in agendamentos_do_dia:
                    
                    inicio_agendado = agendamento.data_e_horario_inicio.replace(tzinfo=None)
                    fim_agendado = agendamento.data_e_horario_fim.replace(tzinfo=None)
                    if inicio_do_slot < fim_agendado and fim_do_slot > inicio_agendado:
                        esta_livre = False; break
                
                if esta_livre:
                    for folga in excecoes_do_dia:
                        inicio_folga = folga.data_inicio.replace(tzinfo=None)
                        fim_folga = folga.data_fim.replace(tzinfo=None)
                        if inicio_do_slot < fim_folga and fim_do_slot > inicio_folga:
                            esta_livre = False; break

                if esta_livre:
                    lista_horarios_livres.append(inicio_do_slot.strftime('%H:%M'))

                inicio_do_slot += timedelta(minutes=30)

        return JsonResponse({'horarios': lista_horarios_livres})
    except Exception as erro:
        return JsonResponse({'erro': str(erro)}, status=500)
    




from django.utils import timezone
from datetime import datetime, timedelta

@login_required
def salvar_agendamento(request):
    
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido.'}, status=405)

    try:
        dados = json.loads(request.body)
        
        id_servico = dados.get('id_servico')
        id_barbeiro = dados.get('id_barbeiro')
        data_str = dados.get('data')
        hora_str = dados.get('hora')

        if not all([id_servico, id_barbeiro, data_str, hora_str]):
            return JsonResponse({'erro': 'Dados incompletos.'}, status=400)

        dt_inicio_naive = datetime.strptime(f"{data_str} {hora_str}", '%Y-%m-%d %H:%M') 


        data_e_horario_inicio = timezone.make_aware(
            dt_inicio_naive, 
            timezone.get_current_timezone()
        ) 

        cliente = Cliente.objects.get(fk_user=request.user) 
        barbeiro = Barbeiro.objects.get(pk=id_barbeiro)
        servico = Servicos.objects.get(pk=id_servico)

        novo_agendamento = Agendamentos(
            fk_cliente=cliente,
            fk_barbeiro=barbeiro,
            fk_servicos=servico,
            data_e_horario_inicio=data_e_horario_inicio 
        )

        novo_agendamento.full_clean() 
        novo_agendamento.save()

        return JsonResponse({'mensagem': 'Agendamento realizado com sucesso!', 'sucesso': True})

    except ValidationError as e:
        
        msg = e.message_dict if hasattr(e, 'message_dict') else str(e)
        return JsonResponse({'erro': msg}, status=400)
    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)