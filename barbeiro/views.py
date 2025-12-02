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

    # GET: Exibe a tela
    if request.method == 'GET':
        if hasattr(request.user, 'clientao'):
            return redirect('/clientes/dashboard/')
        if not hasattr(request.user, 'barber'):
            return redirect('/')
            
        contexto = {'barbeiro_tal': request.user} 
        return render(request, 'barbeiro/editar-perfil.html', contexto)

    # POST: Salva as alterações
    if request.method == 'POST':
        
        # Carrega o form com os dados enviados E o usuário atual (instance)
        form = EditarPerfilBarbeiroForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            # 1. Prepara o User sem salvar ainda
            user = form.save(commit=False)
            
            # 2. Verifica se existe NOVA senha para salvar
            nova_senha = form.cleaned_data.get('nova_senha')
            if nova_senha:
                user.set_password(nova_senha)
                update_session_auth_hash(request, user) # Mantém logado
            
            # 3. Salva User (Nome, Telefone, Email, Senha se mudou)
            user.save()

            # 4. Salva a Foto (se foi enviada)
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
            # Pegamos todos os erros do formulário no formato "bruto".
            # Cada item da dict tem: campo -> [lista de ValidationErrors]
            errors = form.errors.as_data()

            # Mensagem padrão caso não consigamos pegar uma mensagem específica
            msg_erro = "Erro desconhecido."

            # Percorremos os erros (campo por campo)
            for field, error_list in errors.items():

                # error_list é uma lista de ValidationErrors.
                # Vamos pegar APENAS o primeiro erro dessa lista.
                error_obj = error_list[0]

                # Alguns erros possuem atributo .message (erro único)
                # Outros possuem .messages (lista de mensagens)
                # Por isso tratamos ambos os casos:
                if hasattr(error_obj, 'message'):
                    # Caso o erro tenha .message (mais comum nos nossos clean_x())
                    msg_erro = error_obj.message

                elif hasattr(error_obj, 'messages'):
                    # Caso tenha .messages (lista), pegamos a primeira mensagem
                    msg_erro = error_obj.messages[0]

                # Paramos após o primeiro erro
                break

            # Enviamos o erro para o frontend em formato JSON
            return JsonResponse({'error': msg_erro}, status=400)