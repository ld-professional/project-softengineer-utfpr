
from django import forms
from django.core.exceptions import ValidationError
from .models import UserPersonalizado

class CadastroClienteForm(forms.Form):
    
   
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    telefone = forms.CharField(required=True)
    password = forms.CharField(min_length=8,required=True)
    password_confirm = forms.CharField(min_length=8,required=True)
                            

    def clean_email(self):
         
        email_input = self.cleaned_data.get('email')

        if email_input:
           
            email_limpo = email_input.strip().lower()

            
            if UserPersonalizado.objects.filter(email=email_limpo).exists():
                raise ValidationError("Este e-mail já está cadastrado.")
            
            return email_limpo
        
        return email_input 


    def clean_username(self):

        username = self.cleaned_data.get('username')
        if len(username) > 33:
            raise ValidationError("O nome de usuário deve ter no maximo 33 caracteres (contando os espaços.)")
            # nem adianta isso mas coloquei, qp por ja ter tal regra no models. ele roda antes e nem chega aqui

        if any(char.isdigit() for char in username):
            raise ValidationError("O nome de usuário não pode conter números.")


        if UserPersonalizado.objects.filter(username=username).exists():

            raise ValidationError("Este nome de usuário já está em uso.")
        
        return username

    def clean_telefone(self):

        telefone_input = self.cleaned_data.get('telefone')

        telefone_limpo = ''.join(filter(str.isdigit, str(telefone_input)))

        if UserPersonalizado.objects.filter(telefone=telefone_limpo).exists():
            raise ValidationError("Este telefone já está cadastrado.")
        
       
        if len(telefone_limpo) != 11:
             raise ValidationError("O telefone deve ter 11 dígitos (DDD + Número).")
        
        return telefone_limpo



    def clean(self):
        
        dic_limpo = super().clean() 
        
        senha1 = dic_limpo.get('password')
        senha2 = dic_limpo.get('password_confirm')

        if senha1 and senha2:
            if senha1 != senha2:
                raise ValidationError("As senhas digitadas não conferem.")
               
        return dic_limpo