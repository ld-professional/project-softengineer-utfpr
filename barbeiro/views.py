from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
import core.constantes as t


@login_required(login_url='/account/login/')
def barbeiro_dashboard(request):
        
    if  hasattr(request.user, 'clientao'):
        return redirect('/clientes/dashboard/')

    if not hasattr(request.user, 'barber'):

        return redirect('/')

    return render(request,t.BARBEIRO_DASHBOARD) 