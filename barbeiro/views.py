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
from django.db import IntegrityError
from django.contrib.auth import update_session_auth_hash # p/manter o cookie no navegador, atualizado com as novas infos
                                                         # username/ telefone ou email q seja oq foi usado p login,
                                                         #  e senha, atualizados
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import IntegrityError
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie

# Importe o form que criamos
from .forms import EditarPerfilBarbeiroForm

@ensure_csrf_cookie
@login_required(login_url='/account/login/')
def barbeiro_perfil(request):

    # --- GET: Apenas exibe a tela ---
    if request.method == 'GET':
        if hasattr(request.user, 'clientao'):
            return redirect('/clientes/dashboard/')
        if not hasattr(request.user, 'barber'):
            return redirect('/')
            
        # Não precisamos passar o 'form' para o template porque 
        # seu HTML é feito na mão. Passamos o user para preencher os values.
        contexto = {'barbeiro_tal': request.user} 
        return render(request, 'barbeiro/editar-perfil.html', contexto)


    # --- POST: Processa a validação e o salvamento ---
    if request.method == 'POST':
        
        # Instanciamos o form com os dados (POST) e arquivos (FILES)
        # instance=request.user diz: "Isso é uma EDIÇÃO desse usuário", não uma criação.
        form = EditarPerfilBarbeiroForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            # 1. Prepara o User (commit=False para não salvar ainda)
            user = form.save(commit=False)
            
            # 2. Verifica se teve troca de senha (logica processada no form.clean)
            nova_senha = form.cleaned_data.get('nova_senha')
            if nova_senha:
                user.set_password(nova_senha)
                # Atualiza a sessão para não deslogar
                update_session_auth_hash(request, user)
            
            # 3. Salva as alterações do User no Banco (Nome, Email, Telefone, Senha)
            user.save()

            # 4. Salva a Foto (Tabela Barbeiro) manualmente
            # O campo foto_barbeiro não é do model User, então form.save() ignora ele.
            # Pegamos do cleaned_data onde o form já validou se é imagem mesmo.
            nova_foto = form.cleaned_data.get('foto_barbeiro')
            
            if nova_foto:
                barbeiro = user.barber
                barbeiro.foto_barbeiro = nova_foto
                barbeiro.save()

            return JsonResponse({
                'message': 'Perfil atualizado com sucesso!',
                'redirect_url': '/barbeiro/perfil/'
            })
        
        else:
            # Se houver erro (telefone duplicado, senha errada, etc)
            # Pegamos o primeiro erro para mostrar no seu alert
            errors = form.errors.as_data()
            msg_erro = "Erro de validação."
            
            # Loop simples para pegar a primeira mensagem de erro real
            for field, error_list in errors.items():
                # error_list[0] é o objeto erro, .message é o texto dele
                msg_erro = f"{error_list[0].message}"
                break 

            return JsonResponse({'error': msg_erro}, status=400)