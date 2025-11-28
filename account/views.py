from django.shortcuts import render,redirect
from django.http import JsonResponse
import json
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login

import core.constantes as t
 






@ensure_csrf_cookie
def login_view(request):
    
        
    if request.method == 'GET':
        return render(request,t.LOGIN) 
                                            
                                                 
    if request.method == 'POST':

        try:
            dicionario=json.loads(request.body)
            
            
            identificador_front = dicionario.get('identifier') 
            senha_front = dicionario.get('password')

          
            user = authenticate(request, username=identificador_front, password=senha_front)                                                                                   
                                                                                            
            if user is not None:
                         
                login(request, user) 

                if  hasattr(request.user, 'barber'):
                    return JsonResponse({'status': 'ok', 'redirect_url': '/barbeiro/dashboard/'})     

                return JsonResponse({'status': 'ok', 'redirect_url': '/clientes/dashboard/'})     

            else:
                
                return JsonResponse({'error': 'Usuário ou senha incorretos.'}, status=400)

        except Exception as e:

            return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)
        






from .forms import CadastroClienteForm
from django.db import transaction
from .models import  UserPersonalizado 
from clientes.models import Cliente

from django.contrib.auth import login

@ensure_csrf_cookie
def signup_view(request):

    if request.method == 'GET':
        return render(request,t.CADASTRO) 
    
    try: 
        if request.method == 'POST':
            
            dicionario= json.loads(request.body)

            formulario= CadastroClienteForm(dicionario)

            if formulario.is_valid():

                dicionario_limpo = formulario.cleaned_data

                with transaction.atomic():

                    novo_user= UserPersonalizado.objects.create_user(
                        username=dicionario_limpo['username'],
                        telefone=dicionario_limpo['telefone'],
                        email=dicionario_limpo['email'],
                        password=dicionario_limpo['password'],
                    )

                    Cliente.objects.create(fk_user=novo_user)

                login(request,novo_user) 
                                        

                return JsonResponse({'status': 'ok', 'redirect_url': '/clientes/dashboard/'})

            else:               
            
                erros_string = formulario.errors.as_json()
                
                erros_dict = json.loads(erros_string)
  
                return JsonResponse({'errors': erros_dict}, status=400)

    except Exception as e: 
        
        return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)
    







import json
from django.http import JsonResponse
from django.contrib.auth.views import PasswordResetView,PasswordResetConfirmView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from core.settings import EMAIL_HOST_USER

@method_decorator(ensure_csrf_cookie, name='dispatch') # para aplicar decorator em uma classe deve usar name = dispatch
class EsqueceuSenhaView(PasswordResetView):

    # template_name: página "Esqueceu a senha".
    template_name = 'account/forgot-password.html'

    # email_template_name: - Arquivo de texto puro (.txt) usado como fallback para clientes de e-mail que não suportam HTML.
    email_template_name = 'registration/password_reset_email.txt'

    # html_email_template_name: - Arquivo HTML (.html) que define o layout bonito do e-mail.
    html_email_template_name = 'registration/password_reset_email.html'


    # subject_template_name: - Define o assunto do e-mail. - Exemplo: "Redefinir senha no nosso site"
    subject_template_name = 'registration/password_reset_subject.txt'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        email = data.get('email')

        if not email:
            return JsonResponse({'error': 'E-mail é obrigatório.'}, status=400)

        # Cria o formulário padrão do Django com o email recebido
        form = self.form_class({'email': email})

        if form.is_valid():
            # Gera token, UID, monta link e envia o e-mail automaticamente
            form.save(
    request=request,
    use_https=request.is_secure(),
    from_email=EMAIL_HOST_USER,
    html_email_template_name=self.html_email_template_name
)
            return JsonResponse({'message': 'Se o e-mail existir, um link foi enviado.'})

        return JsonResponse({'error': 'E-mail inválido.'}, status=400)








@method_decorator(ensure_csrf_cookie, name='dispatch')
class NovaSenhaView(PasswordResetConfirmView):

    # template_name: É a pagina,O Django já chega aqui sabendo quem é o usuário, pois a URL contém uidb64 e token.
    template_name = 'account/confirm-new-password.html'


    # ---------------------------------------------------------
    # POST:
    # - Recebe JSON do seu fetch() contendo a nova senha.
    # - Monta o formulário interno do Django (SetPasswordForm).
    # - Já valida complexidade da senha.
    # - Se tudo OK → salva no banco e invalida o token.
    # ---------------------------------------------------------
    def post(self, request, *args, **kwargs):
        try:
            # 1. Recebe o JSON (agora contendo new_password1 e new_password2)
            dados_json = json.loads(request.body)

            # 2. Pega a configuração nativa (usuário, token, etc)
            kwargs_form = self.get_form_kwargs()
            
            # 3. Injeta o JSON direto no formulário!
            # Como o JS agora manda os nomes certos, não precisamos traduzir nada.
            kwargs_form['data'] = dados_json

            # 4. Cria o formulário
            form = self.get_form_class()(**kwargs_form)

            # 5. Valida e Salva
            if form.is_valid():
                form.save()
                return JsonResponse({'message': 'Senha alterada com sucesso!'})

            # Retorna erros (Ex: "As senhas não conferem")
            return JsonResponse({'errors': form.errors}, status=400)

        except Exception as e:
            return JsonResponse({'error': f'Erro interno: {str(e)}'}, status=500)   