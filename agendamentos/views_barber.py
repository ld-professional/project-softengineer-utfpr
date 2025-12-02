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
    









@login_required
@ensure_csrf_cookie
def barbeiro_visualizar_agenda(request):
    
    if hasattr(request.user, 'clientao'):
        return redirect('/clientes/dashboard/')

    if not hasattr(request.user, 'barber'):
        return redirect('/account/login')
    
    if request.method == 'GET': 
        # Busca os horários já cadastrados para exibir na lista da direita (HTML)
        # Estou enviando como 'lista_horarios'. 
        # ATENÇÃO: No seu HTML você terá que mudar o loop de {% for s in servicos %} para {% for h in lista_horarios %}
        list_horarios_trab = Horarios_de_trabalho.objects.filter(
            fk_barbeiro=request.user.barber
        ).order_by('dia_semana', 'hora_inicio')

        contexto = {
            'lista_horarios': list_horarios_trab,
        }

        return render(request, 'agendamentos/lista-horarios-trab.html', contexto)



from django.db import transaction
from django.core.exceptions import ValidationError as ErroValidacaoModel
from .forms import FormularioAgenda

@login_required
@ensure_csrf_cookie
def barbeiro_editar_agenda(request):
    
    # 1. Segurança: Bloqueia quem não é barbeiro
    if hasattr(request.user, 'clientao'):
        return JsonResponse({'sucesso': False, 'mensagem': 'Acesso negado.'}, status=403)

    if not hasattr(request.user, 'barber'):
        return JsonResponse({'sucesso': False, 'mensagem': 'Apenas barbeiros podem editar agenda.'}, status=403)

    if request.method == 'POST':
        try:
            # 2. Recebe o JSON enviado pelo JavaScript
            # Exemplo de entrada: {"dias_semana": ["0", "2"], "horario_inicio": "08:00", "horario_fim": "12:00"}
            dados_recebidos = json.loads(request.body)
            
            # 3. Passa para o Forms validar formato e coerência (Início < Fim)
            formulario = FormularioAgenda(dados_recebidos)

            if formulario.is_valid():
                # --- SUCESSO NA VALIDAÇÃO BÁSICA ---
                
                # Pegamos os dados já limpos e convertidos
                # A lista 'dias_semana' agora é [0, 2] (números inteiros), graças ao coerce=int do form
                lista_dias_inteiros = formulario.cleaned_data['dias_semana']
                hora_inicio_limpa = formulario.cleaned_data['horario_inicio']
                hora_fim_limpa = formulario.cleaned_data['horario_fim']
                
                barbeiro_logado = request.user.barber

                # 4. Gravação no Banco de Dados (Com Proteção Atômica)
                # 'atomic': Se der erro em UM dia, ele desfaz TODOS. Evita agenda pela metade.
                with transaction.atomic():
                    
                    for dia_numero in lista_dias_inteiros:
                        
                        # Cria o objeto na memória
                        novo_horario = Horarios_de_trabalho(
                            fk_barbeiro=barbeiro_logado,
                            dia_semana=dia_numero, # Já é inteiro (0 a 6)
                            hora_inicio=hora_inicio_limpa,
                            hora_fim=hora_fim_limpa
                        )

                        # 5. Chama a regra de negócio do seu MODELS.PY
                        # O método .full_clean() vai verificar se existem agendamentos conflitando.
                        novo_horario.full_clean()
                        
                        # Se passou do full_clean, salva de verdade.
                        novo_horario.save()

                return JsonResponse({'sucesso': True, 'mensagem': 'Horários salvos com sucesso!'})

            else:
                # --- ERRO NO FORMULÁRIO (Ex: Hora fim menor que início) ---
                lista_erros_texto = []
                for campo, erros in formulario.errors.items():
                    # Formata a mensagem: "horario_inicio: Campo obrigatório"
                    lista_erros_texto.append(f"{erros[0]}")
                
                return JsonResponse({'sucesso': False, 'mensagem': "\n".join(lista_erros_texto)})

        except ErroValidacaoModel as erro_do_banco:
            # --- ERRO DE REGRA DE NEGÓCIO (Conflito de Agendamento) ---
            # Captura a mensagem "Ação bloqueada! O agendamento do cliente X..." que você fez no models.py
            mensagem_final = ""
            if hasattr(erro_do_banco, 'message_dict'):
                for lista_msgs in erro_do_banco.message_dict.values():
                    mensagem_final += "\n".join(lista_msgs)
            else:
                mensagem_final = str(erro_do_banco)
            
            return JsonResponse({'sucesso': False, 'mensagem': mensagem_final})

        except Exception as erro_generico:
            # --- ERRO INESPERADO (Bug de código ou JSON malformado) ---
            return JsonResponse({'sucesso': False, 'mensagem': f'Erro interno: {str(erro_generico)}'}, status=500)

    # Se tentar acessar via GET ou outro método
    return JsonResponse({'sucesso': False, 'mensagem': 'Método não permitido.'}, status=405)





from django.views.decorators.http import require_POST



@login_required
@require_POST
def barbeiro_excluir_horario(request):
    """
    Endpoint API para exclusão de um único bloco de Horarios_de_trabalho.
    Dispara o método delete() do modelo, que valida conflitos de agendamento.
    """
    
    if not hasattr(request.user, 'barber'):
        return JsonResponse({'sucesso': False, 'mensagem': 'Permissão negada.'}, status=403)

    try:
        # Tenta carregar o JSON (Ponto de falha comum que causa erro no front)
        dados = json.loads(request.body)
        id_horario = dados.get('id_horario')
        
        if not id_horario:
            return JsonResponse({'sucesso': False, 'mensagem': 'ID do horário não fornecido.'}, status=400)

        # 1. Busca o objeto de horário e verifica a permissão
        horario_a_excluir = Horarios_de_trabalho.objects.get(
            pk=id_horario, 
            fk_barbeiro=request.user.barber
        )

        # 2. Executa a exclusão, que dispara o método delete() do Model
        with transaction.atomic():
            # Chamamos o delete() do Model, que tem a lógica de validação de agendamentos futuros
            horario_a_excluir.delete()

        return JsonResponse({'sucesso': True, 'mensagem': 'Turno de trabalho excluído com sucesso!'}, status=200)

    except json.JSONDecodeError:
         # Captura se o body não for um JSON válido
         return JsonResponse({'sucesso': False, 'mensagem': 'JSON inválido na requisição.'}, status=400)

    except Horarios_de_trabalho.DoesNotExist:
        return JsonResponse({'sucesso': False, 'mensagem': 'Horário não encontrado ou você não tem permissão.'}, status=404)
    
    except ErroValidacaoModel as erro_modelo:
        # Captura o erro do Models.py sobre conflito de agendamento
        mensagem_erro = str(erro_modelo)
        return JsonResponse({'sucesso': False, 'mensagem': mensagem_erro}, status=400)
        
    except Exception as e:
        # Captura qualquer erro de código inesperado e garante que o JS receba JSON
        return JsonResponse({'sucesso': False, 'mensagem': f'Erro interno: {type(e).__name__} - {str(e)}'}, status=500)





@login_required
@ensure_csrf_cookie
def barbeiro_exceccao(request):
    
    if  hasattr(request.user, 'clientao'):
        return redirect('/clientes/dashboard/')

    if not hasattr(request.user, 'barber'):
        return redirect('/account/login')
    


    if request.method == 'GET': 

#        lista_excecao_do_cliente = Excecoes.objects.filter(
#            fk_barbeiro__fk_user=request.user,
#        ).order_by('data_e_horario_inicio')
#
#        contexto = {'agendamentos': lista_excecao_do_cliente}

        return render(request, 'agendamentos/excecao.html') 