from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
import json
from .models import Servicos

    

@login_required
@ensure_csrf_cookie
def excluir_servicos(request):

    if  hasattr(request.user, 'clientao'):
        return redirect('/clientes/dashboard/')

    if not hasattr(request.user, 'barber'):
        return redirect('/account/login')

    if request.method == 'POST':

        data= json.loads(request.body)
        id_servico_selecionado= data['id_agendamentos']

        if id_servico_selecionado == None:
            return JsonResponse ({'status': 'nao existe','error':'selecione algo' })
        
        servico_selecionado=Servicos.objects.get(id_servicos=id_servico_selecionado)

        servico_selecionado.delete()

        return JsonResponse({'status': 'success'})




@login_required
@ensure_csrf_cookie
def barbeiros_editar_servicos(request):


    if hasattr(request.user, 'clientao'):
        return redirect('/clientes/dashboard/')

    if not hasattr(request.user, 'barber'):
        return redirect('/account/login')

    if request.method == 'GET':

        lista_servicos = Servicos.objects.all().order_by('nome_servico')
        
        contexto = {
            'servicos': lista_servicos
        }
        
        return render(request, 'servicos/editar-servicos.html', contexto)
    
    # 2. Lógica para SALVAR (Adicionar ou Editar)
    if request.method == 'POST':
        try:

            id_servico = request.POST.get('id_servico')
            nome = request.POST.get('nome_servico')
            preco = request.POST.get('preco_servico')
            duracao = request.POST.get('slot_duracao_servico')

            if id_servico:

                servico = get_object_or_404(Servicos, pk=id_servico)
                servico.nome_servico = nome
                servico.preco_servico = preco
                servico.slot_duracao_servico = duracao
                servico.save()
            else:

                Servicos.objects.create(
                    nome_servico=nome,
                    preco_servico=preco,
                    slot_duracao_servico=duracao
                )
            

            return redirect('barbeiro_editar_servicos')

        except Exception as e:
            print(f"Erro ao salvar serviço: {e}")

            return redirect('barbeiro_editar_servicos')


