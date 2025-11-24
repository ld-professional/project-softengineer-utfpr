# o fluxo para login eh views -> backends.py o CONTEXTO do strategy/ 
# orquestrador = a) escolher o metodo b) buscar o suposto usuario e senha
#
#entao  backends.py-> loginContratoStrategy.py --> gera strategies.py  ( com emailchecker telefonechecker )
#
#detalhe q o bakcends.py tem uma cnstrucao ctrl c + ctrl v e ele espera receber username 
#
#mas o detalhe eh q username eh so o nome da variavel, e vamos passar para username o identifier

'''
O fluxo é exatamente esse: a View chama a função global authenticate(),
 e o Django internamente procura a sua classe Contexto e executa o método authenticate() que você escreveu nela.
por isso ter este import

'''
from django.shortcuts import render,redirect
from django.http import JsonResponse
import json
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login

import core.constantes as t
 # no get envia o cookie e logo pdoe ser retornado pelo post
@ensure_csrf_cookie
def login_view(request):
    
        #se for GET: Mostra o HTML e GRAVA O COOKIE DE SEGURANÇA
    if request.method == 'GET':
        return render(request,t.LOGIN) # se digitar url vc n envia json entao request eh """null"""
                                            #pois no caso eh o body o corpo do json, pois o resto eh dados de rede, aqui no caso
                                            # estamos devolvend uma repsosta com cookie e devolvendo o html em si
                                            # porem aqui no caso eh nitid oq estamos devolvend oo request ( mesma variavel
                                            #que esta em def login_view) ou seja estamos devolvend orequest um json com cookie

        # 2. O 'request.body' está vazio (não tem JSON), pois é apenas um acesso de URL.
        # 2. A função 'render' usa os dados do request apenas para montar o contexto.
        # 3. O que retorna NÃO É o request, e NÃO É um JSON.
        # 4. O retorno é um objeto 'HttpResponse' contendo HTML Puro.
        
        # O decorator @ensure_csrf_cookie injeta o cookie no CABEÇALHO (Header) desta resposta.
    if request.method == 'POST':

        try:
            dicionario=json.loads(request.body)
            
            # Nomes vindos do seu JS
            identificador_front = dicionario.get('identifier') 
            senha_front = dicionario.get('password')

            # A MÁGICA DA TRADUÇÃO:
            # O JS manda 'identifier', mas o Django exige 'username'.
            # O seu backend 'Contexto' vai receber isso e saber o que fazer.
            user = authenticate(request, username=identificador_front, password=senha_front) # funcao q seria do backends.py
                                                                                            # mas esta eh a global q usa 
                                                                                            # a do bakcends.py
            if user is not None:
                
                # 1. A SESSÃO (Mexe no HEADER da resposta)
                login(request, user) 
                # O que essa linha faz nos bastidores:
                # A) Cria uma linha na tabela 'django_session' no banco. ligando tal user
                # B) Avisa o Django para colocar um adesivo na resposta responsejson 
                #   q sera enviada: "Set-Cookie: sessionid=xyz..."
                # C) O navegador vai ler esse adesivo (Header) e guardar o cookie sozinho. O JS nem vê.


                # 2. O DADO VISUAL (Mexe no BODY da resposta)
                return JsonResponse({'status': 'ok', 'redirect_url': '/clientes/dashboard/'}) # aqui trabalha com roteamento
                # O 'JsonResponse' cria o corpo da mensagem.
                # Basicamente: "Aqui estão os dados escritos que o JavaScript pediu".
                # O seu JS (fetch) vai ler APENAS esta parte aqui para saber o link de redirecionamento.


            else:
                # so roda se n der erro no try e logo o try tem return mas n cehga nele se if for falso
                # logo return erro aqui
                return JsonResponse({'error': 'Usuário ou senha incorretos.'}, status=400)



        except Exception as e:

            return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)
        

# para cadastro obvio usar o forms.py para a validacao

from .forms import CadastroClienteForm
from django.db import transaction
from .models import  UserPersonalizado # CriadorUser n eh a fabrica pq ela eh pro caso igual dito pelo terminal ou admin.
from clientes.models import Cliente

from django.contrib.auth import login

@ensure_csrf_cookie
def signup_view(request):

    if request.method == 'GET':
        return render(request,t.CADASTRO) # sem a barra inicial
    
    try: 
        if request.method == 'POST':
            
            dicionario= json.loads(request.body)

            formulario= CadastroClienteForm(dicionario)

            if formulario.is_valid():
                
                # se os dados estao validos, salvar eles limpos no dicionario limpo
                dicionario_limpo = formulario.cleaned_data
                # lembrando q cleaned data eh uma variavel herdada, msm q no formulario tenha uma variavel local de msm nome
                # logo la no formulario pdoe ter ate outro noem como form_limpo


                # agora para escrever num arquivo usamos o proprio with, pq vms escrever no banco de dadps
                with transaction.atomic():

                    # criar o novo user pela fabrica:
                    novo_user= UserPersonalizado.objects.create_user(
                        username=dicionario_limpo['username'],
                        telefone=dicionario_limpo['telefone'],
                        email=dicionario_limpo['email'],
                        password=dicionario_limpo['password'],
                    )

                    Cliente.objects.create(fk_user=novo_user)

                login(request,novo_user) # para devovler ao somente ao, navegador o session id, no proximo repsonse
                                        # onde tal pagina ja ira cehcar se tem um session id, e n ocaso tem pq ele fez login

                return JsonResponse({'status': 'ok', 'redirect_url': '/clientes/dashboard/'})

            else:
                # sobre o if de is valid, ou seja, erro de validacao, q no caso o forms, devolve qual seja o erro
                # email ja eiste, ou nao preenchido campo X... e o javascript fica repsonsavel por pegar cada erro
                # e pra cada erro acumular numa variavel e imprimir em cada campo o erro...

                # 1. Pega a string de erro do Django
                erros_string = formulario.errors.as_json()
                
                # 2. Transforma (Parser) de String para Dicionário Python
                erros_dict = json.loads(erros_string)

                # 3. Envia o Dicionário. O JsonResponse vai criar um JSON limpo.
                return JsonResponse({'errors': erros_dict}, status=400)

    except Exception as e: # onde exception eh qlqer erro e imprime o erro
        # se nao entrou em nenhum dos if, entao eh erro tecncio logo devolver erro status =500 q devovle a pagina de erro 500
        return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)
    

    # exatametne e no js:

    '''
    
    if (result.errors) {
    // 1. Detecta a chave 'errors' vinda do json q chamei ali no return de error
    // 2. JSON.parse converte a string do Django em objeto JS
    const errorData = typeof result.errors === 'string' ? JSON.parse(result.errors) : result.errors;
    // 3. Pega as mensagens e mostra
    const errorList = Object.values(errorData).flat().map(err => err.message || err);
    error_message.innerText = errorList.join(". ");
    
    ou para o erro de  status= 500:

    } else {
    // Se não achou 'result.errors', ele cai aqui.
    // Ele procura a chave 'error' (singular) e mostra o texto direto.
    error_message.innerText = result.error || result.mensagem || 'Erro ao processar.';
}

e mantem logo no msm html...
    '''



# ==============================================================================
#  COLE ISTO NO FINAL DO ARQUIVO account/views.py
# ==============================================================================

# --- IMPORTS NECESSÁRIOS PARA A RECUPERAÇÃO DE SENHA ---
# default_token_generator: A ferramenta que cria e verifica o "crachá" (token) de segurança.
# urlsafe_base64_decode: Decodifica o ID do usuário que vem "escondido" na URL (ex: 'Mg' -> 5).
# PasswordResetForm: Formulário nativo do Django que valida email e envia a mensagem.
# SetPasswordForm: Formulário nativo que valida a força da senha e faz a criptografia (hash).
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from .models import UserPersonalizado  # Importando seu modelo DIRETAMENTE, sem get_user_model()

# ---------------------------------------------------------
# VIEW 1: ESQUECEU A SENHA
# Objetivo: Receber o e-mail do usuário e enviar o link de recuperação.
# ---------------------------------------------------------
@ensure_csrf_cookie
def esqueceu_senha(request):
    
    # 1. Se for GET: Apenas mostra a tela para digitar o e-mail
    if request.method == 'GET':
        # Renderiza o HTML do formulário
        return render(request, 'account/forgot-password.html') 

    # 2. Se for POST: Processa o envio
    if request.method == 'POST':
        try:
            # Lê o JSON enviado pelo JavaScript
            data = json.loads(request.body)
            
            # 'PasswordResetForm' é uma classe do Django que faz duas coisas:
            # A) Valida se o campo é um e-mail válido.
            # B) Verifica se existe algum usuário ativo com esse e-mail.
            form = PasswordResetForm(data)
            
            if form.is_valid():
                # Se o e-mail for válido, o método .save() faz a mágica:
                # 1. Gera um token único para esse usuário.
                # 2. Monta o link apontando para a URL chamada 'nova_senha' (no urls.py).
                # 3. Envia o e-mail para o usuário.
                form.save(
                    request=request,
                    use_https=request.is_secure(), # Usa HTTPS se disponível (segurança)
                    email_template_name='registration/password_reset_email.html', 
                    subject_template_name='registration/password_reset_subject.txt'
                )
                # Retornamos sucesso sempre. Por segurança, não avisamos "esse email não existe"
                # para evitar que hackers descubram quem tem conta no site.
                return JsonResponse({'message': 'Se o e-mail existir, um link foi enviado.'})
            else:
                return JsonResponse({'error': 'E-mail inválido ou obrigatório.'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# ---------------------------------------------------------
# VIEW 2: NOVA SENHA (O Link Clicado)
# Objetivo: Validar o link clicado e salvar a nova senha.
# ---------------------------------------------------------
# Os parâmetros <uidb64> e <token> chegam aqui AUTOMATICAMENTE vindos da URL.
@ensure_csrf_cookie
def nova_senha(request, uidb64=None, token=None):
    
    # --- PASSO 1: Descobrir QUEM é o usuário ---
    try:
        # O ID vem codificado na URL (ex: "Mg").
        # Decodificamos de volta para número/texto (ex: "5").
        uid = force_str(urlsafe_base64_decode(uidb64))
        
        # Buscamos no SEU banco de dados se esse ID existe.
        user = UserPersonalizado.objects.get(pk=uid)
        
    except (TypeError, ValueError, OverflowError, UserPersonalizado.DoesNotExist):
        # Se o código da URL estiver quebrado ou o usuário foi deletado
        user = None

    # --- PASSO 2: Validar a Permissão (Token) ---
    # O 'check_token' verifica:
    # A) Esse token pertence a esse usuário?
    # B) O token ainda está no prazo de validade (padrão: dias)?
    # C) O usuário já mudou a senha DEPOIS de gerar esse token? (Se sim, o link morre).
    if user is not None and default_token_generator.check_token(user, token):
        
        # CENÁRIO A: Usuário clicou no link (GET) -> Mostra o formulário de senha
        if request.method == 'GET':
            return render(request, 'account/confirm-new-password.html')
        
        # CENÁRIO B: Usuário digitou a senha e enviou (POST) -> Salva no banco
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                senha_nova = data.get('password')

                # 'SetPasswordForm' é a classe do Django que:
                # 1. Valida regras de senha (tamanho, complexidade, etc).
                # 2. Prepara a criptografia (hash).
                # Passamos a mesma senha 2x porque seu JS já garantiu que são iguais.
                form = SetPasswordForm(user, {'new_password1': senha_nova, 'new_password2': senha_nova})
                
                if form.is_valid():
                    form.save() # Salva a senha criptografada e INVALIDA o token usado (segurança).
                    return JsonResponse({'message': 'Senha alterada com sucesso!'})
                else:
                    # Se o Django achar a senha fraca, devolvemos o erro detalhado
                    erros_dict = json.loads(form.errors.as_json())
                    return JsonResponse({'errors': erros_dict}, status=400)

            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
    
    else:
        # --- PASSO 3: Link Inválido ---
        # Se o token expirou, já foi usado ou a URL está errada.
        # Redireciona para a Home para não dar erro de tela branca.
        return redirect('/')