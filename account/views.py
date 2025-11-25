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
    

    


from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from .models import UserPersonalizado  



@ensure_csrf_cookie
def esqueceu_senha(request):
    
    
    if request.method == 'GET':
        
        return render(request, 'account/forgot-password.html') 

    
    if request.method == 'POST':
        try:
            
            data = json.loads(request.body)
          
            form = PasswordResetForm(data)
            
            if form.is_valid():
                
               
                form.save(
                    request=request,
                    use_https=request.is_secure(), 
                    email_template_name='registration/password_reset_email.html', 
                    subject_template_name='registration/password_reset_subject.txt'
                )
                
                
                return JsonResponse({'message': 'Se o e-mail existir, um link foi enviado.'})
            else:
                return JsonResponse({'error': 'E-mail inválido ou obrigatório.'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@ensure_csrf_cookie
def nova_senha(request, uidb64=None, token=None):
    
    try:
            
        uid = force_str(urlsafe_base64_decode(uidb64))
        
        
        user = UserPersonalizado.objects.get(pk=uid)
        
    except (TypeError, ValueError, OverflowError, UserPersonalizado.DoesNotExist):
        
        user = None
 
    if user is not None and default_token_generator.check_token(user, token):
        
        if request.method == 'GET':
            return render(request, 'account/confirm-new-password.html')
        
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                senha_nova = data.get('password')


                form = SetPasswordForm(user, {'new_password1': senha_nova, 'new_password2': senha_nova})
                
                if form.is_valid():
                    form.save() 
                    return JsonResponse({'message': 'Senha alterada com sucesso!'})
                else:

                    erros_dict = json.loads(form.errors.as_json())
                    return JsonResponse({'errors': erros_dict}, status=400)

            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
    
    else:

        return redirect('/')