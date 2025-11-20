from django.shortcuts import render,redirect 
# Create your views here.

def pagina_inicial_home(request):
    """
    Esta view simplesmente renderiza a página principal (home).
    """
    # Retorna o template localizado em 'templates/core/home.html'
    return render(request, 'global/home.html')

def verficacao_login_agendar(request):
# O Django já sabe automaticamente se o user tem o cookie sessionid válido atraves do request.user.is_autenticate

    if request.user.is_authenticated:
        return redirect('/clientes/dashboard/')
    else:
        # Se não tem, manda pro Login
        return redirect('/account/login/')
    


    #redirect: 
    #          - basicamente se fosse render, o usuario ao clicar em agendar receberia um json com caminho
                # como em login sendo uma chave pro caminho, mas como n trabalharemso com json basicametne
                # ja forcamos sem necessidade do JS fazer o if cahve_caminho e redirecionar pro html do caminho
                # pelo proprio django

'''
Fluxo via JS (Login): O servidor manda JSON {url: '/dashboard'} -> O JS lê -> O JS redireciona.

Fluxo via Redirect (Botão): O servidor manda um código HTTP 302 -> O Navegador (sozinho)
 lê e muda de página imediatamente. O JS nem fica sabendo.

 O render normalmente devolve HTML, não JSON. Quem devolve JSON é o JsonResponse.
   Mas a ideia de que "o redirect evita o trabalho manual do JS" está certíssima.

'''