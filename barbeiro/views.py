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


import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import IntegrityError

@ensure_csrf_cookie
@login_required(login_url='/account/login/')
def barbeiro_perfil(request):

    # GET: Renderiza a página HTML
    if request.method == 'GET':

        if hasattr(request.user, 'clientao'):

            return redirect('/clientes/dashboard/')
        
        if not hasattr(request.user, 'barber'):

            return redirect('/')
            
        contexto = {'barbeiro_tal': request.user}
        
        return render(request, 'barbeiro/editar-perfil.html', contexto)

    # POST: Processa os dados via AJAX/Fetch
    if request.method == 'POST':
        try:
            user = request.user
            barbeiro = user.barber
            
            # Nota: Ao usar FormData no JS, os dados vêm em request.POST normalmente
            novo_username = request.POST.get('username')
            novo_email = request.POST.get('email')
            novo_telefone = request.POST.get('telefone')

            # Validações básicas de Backend
            if not novo_username or not novo_email or not novo_telefone:
                return JsonResponse({'error': 'Todos os campos são obrigatórios.'}, status=400)

            # Limpeza do telefone
            telefone_limpo = ''.join(filter(str.isdigit, str(novo_telefone)))

            # Atualiza User
            user.username = novo_username
            user.email = novo_email
            user.telefone = telefone_limpo
            user.save()

            # Atualiza Foto (request.FILES)
            if 'foto_barbeiro' in request.FILES:
                barbeiro.foto_barbeiro = request.FILES['foto_barbeiro']
                barbeiro.save()

            # Retorna sucesso e a nova URL da imagem para atualizar na hora se quiser
            return JsonResponse({
                'message': 'Perfil atualizado com sucesso!',
                'redirect_url': '/barbeiro/perfil/' # ou onde você quiser redirecionar
            })

        except IntegrityError:
            return JsonResponse({'error': 'Nome de usuário ou telefone já estão em uso.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)

