#regra de ouro da segurança web é: "Nunca confie no Front-end".

# Validação no JS (Front-end): É para Experiência do Usuário (UX).

# Serve para dar feedback instantâneo ("Ei, as senhas não batem") sem precisar recarregar a página ou esperar o servidor.

from django import forms
from django.core.exceptions import ValidationError
from .models import UserCustomizado

class CadastroClienteForm(forms.Form):
    
    # 1. Definição dos Campos q devem vir do json, onde os campos/ chaves devem ter exatametne o msm nome destas vairavies
    username = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    telefone = forms.CharField(required=True)
    password = forms.CharField(min_length=8,required=True)
    password_confirm = forms.CharField(min_length=8,required=True)
                            # se n foi digitado, estiver null o required ja mata e devolve erro..
                            # ja adiciona o tamanho ser no minimo 8 aqui do q n odef clean geral 

    #  2. Validações Individuais  roda primeiro e salvam numa variavel global chamada cleaned_data

    def clean_email(self):

        email = self.cleaned_data.get('email')

        if UserCustomizado.objects.filter(email=email).exists():

            raise ValidationError("Este e-mail já está cadastrado.")
        

        return email # retorna o conteudo da variavel email, para a chave do cleaned data




    def clean_username(self):
        username = self.cleaned_data.get('username')
        if UserCustomizado.objects.filter(username=username).exists():
            raise ValidationError("Este nome de usuário já está em uso.")
        return username

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if UserCustomizado.objects.filter(telefone=telefone).exists():
            raise ValidationError("Este telefone já está cadastrado.")
        return telefone

    #  3. Validação Geral (clean): auqi eh o is_valid() ele roda primeiro cada validacao acima
                                    # e entao roda este clean q eh geral onde fica validacoes complexas como o def clean 
                                    # de cada objeto, mas como fizemso no proprio models. deixamos la e dps no views
                                    # chamamos o clean do objeto por la
                                    #e entao aqui fica o basico q seria se paswword confirm == apssword,
    def clean(self):
        # AQUI ESTÁ A MUDANÇA QUE VOCÊ PEDIU:
        # Pegamos o dicionário pronto do 'Pai' e guardamos na variável 'dic_limpo'
        dic_limpo = super().clean() 
        
        # Agora usamos 'dic_limpo' para pegar os valores
        senha1 = dic_limpo.get('password')
        senha2 = dic_limpo.get('password_confirm')

        if senha1 and senha2:
            if senha1 != senha2:
                raise ValidationError("As senhas digitadas não conferem.")
        
        # IMPORTANTE: Temos que retornar o 'dic_limpo' no final
        return dic_limpo