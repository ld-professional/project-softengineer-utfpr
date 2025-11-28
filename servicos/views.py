from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
import json
from .models import Servicos



@login_required
@ensure_csrf_cookie
def barbeiros_visualizar_servicos(request):

    
    if  hasattr(request.user, 'clientao'):
        return redirect('/clientes/dashboard/')

    if not hasattr(request.user, 'barber'):
        return redirect('/account/login')




    if request.method == 'GET':
        lista_servicos = Servicos.objects.all()
        
        contexto = {'servicos': lista_servicos}

        return render(request,'servicos/meus-servicos.html' , contexto)
    

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
