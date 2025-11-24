from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
# Create your views here.
import core.constantes as t

'''

1. O que é o @login_required? (O Porteiro do Prédio)

Ele é um Decorador. Em Python, um decorador é uma função que "embrulha" a sua função.

    Como funciona: Antes da sua função cliente_dashboard rodar, o Django roda o código do @login_required.

    A Lógica dele:

        "Esse usuário tem um sessionid válido nos cookies?"

        NÃO: Interrompe tudo e chuta o usuário para a URL de login (/account/login/).

        SIM: Deixa a sua função cliente_dashboard rodar.

'''


@login_required(login_url='/account/login/') # chuta vc pra onde definiu aqui nos parenteses...
def cliente_dashboard(request):
    
    if  hasattr(request.user, 'barber'):
        return redirect('barbeiro_pagina_inicial_dashboard ')

    if not hasattr(request.user, 'clientao'):
        # Se não for cliente (nem barbeiro),
        # mandamos ele para a home ou para o painel dele.
        return redirect('/account/login')


    if request.method == 'GET':
        return render(request,t.CLIENTE_DASHBOARD) # n pode ter barra !