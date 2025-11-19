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