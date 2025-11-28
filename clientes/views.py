from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required

import core.constantes as t

from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
@login_required(login_url='/account/login/') 
def cliente_dashboard(request):
    
    if  hasattr(request.user, 'barber'):
        return redirect('barbeiro_pagina_inicial_dashboard')

    if not hasattr(request.user, 'clientao'):
        return redirect('/account/login')

    if request.method == 'GET':

        usuario_fulando_de_tal= request.user 
        nome= str(usuario_fulando_de_tal.username).capitalize()
        contexto={'nome_do_cara': nome}

        return render(request,t.CLIENTE_DASHBOARD, contexto) 
    


from django.contrib.auth import logout
from django.http import HttpResponse


@login_required(login_url='/account/login/') 
def logout_view(request):

    if request.method== 'POST':
        logout(request)
        return HttpResponse(status=204)

    
    return redirect('pagina_inicial')
