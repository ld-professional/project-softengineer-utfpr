from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required(login_url='/account/login/')
def barbeiro_dashboard(request):
        
    if  hasattr(request.user, 'clientao'):
        return redirect('/clientes/dashboard/')

    if not hasattr(request.user, 'barber'):
        # Se não for cliente (nem barbeiro),
        # mandamos ele para a home ou para o painel dele.
        return redirect('/')


    if request.method == 'GET':
        return render(request,'barbeiro/dashboard.html') # n pode ter barra !