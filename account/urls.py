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
    


'''
Você teve que colocar name='password_reset_confirm' por um motivo simples: O PasswordResetForm do Django é "programado"
 para procurar esse nome exato.

Vou te explicar o que acontece nos bastidores quando você chama form.save():

    A Geração do E-mail: Quando você executa form.save(), o Django começa a montar o e-mail que será enviado para o usuário.

    A Criação do Link: Dentro desse e-mail, o Django precisa escrever o link clicável
      (algo como seusite.com/nova-senha/Mg/token...). Para construir esse link, o código interno do
        Django faz uma chamada de função parecida com esta:

        # Código interno do Django (simplificado)
        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})

        
O Problema: A função reverse funciona como um GPS: você dá o nome do lugar ('password_reset_confirm')
 e ela te devolve o endereço (/account/nova-senha/...).

    Se no seu urls.py o nome era 'nova_senha', o GPS do Django dizia: "Não conheço nenhum lugar chamado
      'password_reset_confirm'". E aí estourava o erro NoReverseMatch.

    Ao mudar o nome para 'password_reset_confirm', o GPS encontrou a rota e conseguiu gerar o link.  




    É uma convenção do Django. Como você está usando o formulário pronto deles (PasswordResetForm),
      você precisa jogar pelas regras deles e usar o nome de rota que eles esperam encontrar.      
'''