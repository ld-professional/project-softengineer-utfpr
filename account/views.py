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
from django.shortcuts import render
from django.http import JsonResponse
import json
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login


 # no get envia o cookie e logo pdoe ser retornado pelo post
@ensure_csrf_cookie
def login_view(request):
    
        #se for GET: Mostra o HTML e GRAVA O COOKIE DE SEGURANÇA
    if request.method == 'GET':
        return render(request, 'login.html') # se digitar url vc n envia json entao request eh """null"""
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
                return JsonResponse({'status': 'ok', 'redirect_url': '/cliente/dashboard/'})
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
        return render(request,'signup.html')
    
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

                return JsonResponse({'status': 'ok', 'redirect_url': '/cliente/dashboard/'})

            else:
                # sobre o if de is valid, ou seja, erro de validacao, q no caso o forms, devolve qual seja o erro
                # email ja eiste, ou nao preenchido campo X... e o javascript fica repsonsavel por pegar cada erro
                # e pra cada erro acumular numa variavel e imprimir em cada campo o erro...

                return JsonResponse({'errors': formulario.errors.as_json()}, status=400)

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