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
from core.constantes import ESCOLHER_SERVICO, ESCOLHER_BARBEIRO, ESCOLHER_DIA 




def meusagendamentos(request):
    
    if request.method == 'GET': 

        lista_servicos = Servicos.objects.all()

        contexto = {'servicos': lista_servicos}

        return render(request, 'agendamentos/cliente-meus-agendamentos.html', contexto)       

def validar_data_hora_futura(data_obj, hora_str=None):
    hoje = date.today()
    

    if data_obj < hoje:
        return False


    if hora_str and data_obj == hoje:
        hora_obj = datetime.strptime(hora_str, '%H:%M').time()
        agora = datetime.now().time()
        
        if hora_obj < agora:
            return False
            

    return True

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
    contexto = {
        'barbeiros': lista_barbeiros,
        'id_servico_escolhido': id_do_servico
    }
    return render(request, ESCOLHER_BARBEIRO, contexto)

@login_required
@ensure_csrf_cookie
def escolher_dia(request):

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

    return render(request, 'agendamentos/agenda-realizado.html')

@login_required
@require_GET
def buscar_horarios_api(request):
    data_texto = request.GET.get('data')
    id_barbeiro = request.GET.get('id_barbeiro')
    id_servico = request.GET.get('id_servico')

    if not all([data_texto, id_barbeiro, id_servico]):
        return JsonResponse({'erro': 'Faltam dados.'}, status=400)
    
    try:
        data_base = datetime.strptime(data_texto, '%Y-%m-%d').date()

        if not validar_data_hora_futura(data_base):
             return JsonResponse({'horarios': [], 'mensagem': 'Data inválida ou passada.'})

        dia_semana = data_base.weekday()
        
        servico = Servicos.objects.get(pk=id_servico)
        duracao_minutos = servico.slot_duracao_servico * 30 
        
        turnos = Horarios_de_trabalho.objects.filter(
            fk_barbeiro_id=id_barbeiro,
            dia_semana=dia_semana
        ).order_by('hora_inicio')

        if not turnos.exists():
            return JsonResponse({'horarios': [], 'mensagem': 'Barbeiro não trabalha neste dia.'})

        # Busca ocupações convertendo para Timezone Local se necessário no loop
        agendamentos_ocupados = Agendamentos.objects.filter(
            fk_barbeiro_id=id_barbeiro,
            data_e_horario_inicio__date=data_base
        )
        excecoes_ocupadas = Excecoes.objects.filter(
            fk_barbeiro_id=id_barbeiro,
            data_inicio__date__lte=data_base,
            data_fim__date__gte=data_base
        )

        lista_horarios_livres = []
        agora = timezone.localtime()

        for turno in turnos:
            inicio_slot = timezone.make_aware(datetime.combine(data_base, turno.hora_inicio))
            fim_expediente = timezone.make_aware(datetime.combine(data_base, turno.hora_fim))

            while inicio_slot + timedelta(minutes=duracao_minutos) <= fim_expediente:
                fim_slot = inicio_slot + timedelta(minutes=duracao_minutos)
                
                # Regra: Ignorar passado
                if data_base == agora.date() and inicio_slot <= agora:
                    inicio_slot += timedelta(minutes=30)
                    continue

                esta_livre = True

                # Verifica Agendamentos (com conversão de Timezone)
                for ag in agendamentos_ocupados:
                    ag_ini = timezone.localtime(ag.data_e_horario_inicio)
                    ag_fim = timezone.localtime(ag.data_e_horario_fim)

                    if inicio_slot < ag_fim and fim_slot > ag_ini:
                        esta_livre = False
                        break 
                
                # Verifica Exceções
                if esta_livre:
                    for ex in excecoes_ocupadas:
                        ex_ini = timezone.localtime(ex.data_inicio)
                        ex_fim = timezone.localtime(ex.data_fim)

                        if inicio_slot < ex_fim and fim_slot > ex_ini:
                            esta_livre = False
                            break
                
                if esta_livre:
                    lista_horarios_livres.append(inicio_slot.strftime('%H:%M'))

                inicio_slot += timedelta(minutes=30)

        return JsonResponse({'horarios': lista_horarios_livres})

    except Exception as erro:
        return JsonResponse({'erro': str(erro)}, status=500)


@login_required
@require_POST
def salvar_agendamento(request):
    try:
        dados = json.loads(request.body)
        
        id_servico = dados.get('id_servico')
        id_barbeiro = dados.get('id_barbeiro')
        data_str = dados.get('data')
        hora_str = dados.get('hora')

        if not all([id_servico, id_barbeiro, data_str, hora_str]):
            return JsonResponse({'erro': 'Dados incompletos.'}, status=400)



        data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()


        if not validar_data_hora_futura(data_obj, hora_str):
            return JsonResponse({'erro': 'Erro: Tentativa de agendar em data ou horário passado.'}, status=400)



        dt_naive = datetime.strptime(f"{data_str} {hora_str}", '%Y-%m-%d %H:%M') 
        
        data_inicio = timezone.make_aware(dt_naive, timezone.get_current_timezone())

        cliente = get_object_or_404(Cliente, fk_user=request.user)
        barbeiro = get_object_or_404(Barbeiro, pk=id_barbeiro)
        servico = get_object_or_404(Servicos, pk=id_servico)

        novo_agendamento = Agendamentos(
            fk_cliente=cliente,
            fk_barbeiro=barbeiro,
            fk_servicos=servico,
            data_e_horario_inicio=data_inicio
        )

        novo_agendamento.full_clean() 
        novo_agendamento.save()

        return JsonResponse({'mensagem': 'Agendamento realizado com sucesso!', 'sucesso': True})

    except ValidationError as e:
        msg = list(e.messages)[0] if hasattr(e, 'messages') else str(e)
        return JsonResponse({'erro': msg}, status=400)
        
    except Exception as e:
        return JsonResponse({'erro': f"Erro interno: {str(e)}"}, status=500)