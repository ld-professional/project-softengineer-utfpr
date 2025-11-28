from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
import core.constantes as t
from .models import Barbeiro
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
@login_required(login_url='/account/login/')
def barbeiro_dashboard(request):
        
    if  hasattr(request.user, 'clientao'):
        return redirect('/clientes/dashboard/')

    if not hasattr(request.user, 'barber'):

        return redirect('/')
    

    barbeiro_nome=Barbeiro.objects.get(fk_user=request.user)

    contexto= {'nome_barbeiro': barbeiro_nome}

    return render(request,t.BARBEIRO_DASHBOARD,contexto) 