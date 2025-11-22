from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('recuperar-senha/', views.esqueceu_senha, name='esqueceu_senha'),
    

    # URL 2: Onde o usuário digita a nova senha (Endereço Dinâmico)
    # -------------------------------------------------------------------------
    # EXPLICAÇÃO TÉCNICA DOS PARÂMETROS < >:
    #
    # 1. O que são <uidb64> e <token>?
    #    São "Path Converters" (Capturadores de URL).
    #    Eles dizem ao Django: "Não espere um texto fixo aqui. Espere QUALQUER
    #    coisa que o usuário mandar e guarde nessas variáveis".
    #
    # 2. O Processo de "Captura":
    #    Se o usuário acessar: 
    #    www.site.com/account/nova-senha/Mg/abc-123/
    #
    #    O Django vai fatiar a URL automaticamente:
    #    - A parte "Mg" será guardada na variável 'uidb64'.
    #    - A parte "abc-123" será guardada na variável 'token'.
    #
    # 3. Quem valida isso? (Importante!)
    #    O arquivo urls.py NÃO VALIDA NADA. Ele é apenas um "carteiro".
    #    Ele pega o pacote (Mg e abc-123) e entrega na mão da sua View (views.py).
    #
    #    A View (função nova_senha) é quem vai receber esses dados como argumentos:
    #    def nova_senha(request, uidb64='Mg', token='abc-123'):
    #       ...
    #    
    #    Se o usuário digitar "batata" no lugar do token, o urls.py vai aceitar
    #    e passar "batata" para a view. A View é quem vai tentar usar esse token
    #    e descobrir que ele é falso.
    # -------------------------------------------------------------------------
    path('nova-senha/<uidb64>/<token>/', views.nova_senha, name='password_reset_confirm'),
]
    
