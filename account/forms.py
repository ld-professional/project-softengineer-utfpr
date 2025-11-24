#regra de ouro da segurança web é: "Nunca confie no Front-end".

# Validação no JS (Front-end): É para Experiência do Usuário (UX).

# Serve para dar feedback instantâneo ("Ei, as senhas não batem") sem precisar recarregar a página ou esperar o servidor.

from django import forms
from django.core.exceptions import ValidationError
from .models import UserPersonalizado

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
         
        email_input = self.cleaned_data.get('email')

        if email_input:
            # 1. LIMPEZA TOTAL: Tira espaços do começo/fim e transforma em minúsculo
            # Isso garante que 'Joao@Gmail.com ' vire 'joao@gmail.com'
            email_limpo = email_input.strip().lower()

            # 2. VALIDAÇÃO DE EXISTÊNCIA
            # Agora comparamos o e-mail limpo com o que está no banco
            if UserPersonalizado.objects.filter(email=email_limpo).exists():
                raise ValidationError("Este e-mail já está cadastrado.")
            
            # 3. RETORNO
            return email_limpo
        
        return email_input # retorna o conteudo da variavel email, para a chave do cleaned data




    def clean_username(self):
        username = self.cleaned_data.get('username')
        if UserPersonalizado.objects.filter(username=username).exists():
            raise ValidationError("Este nome de usuário já está em uso.")
        return username

    def clean_telefone(self):
        telefone_input = self.cleaned_data.get('telefone')
        
        # 1. LIMPEZA: Remove tudo que não é número
        # (Igual você faz no create_user, tem que fazer aqui também para comparar igual)
        telefone_limpo = ''.join(filter(str.isdigit, str(telefone_input)))

        # 2. VALIDAÇÃO DE EXISTÊNCIA (Agora comparando banana com banana)
        if UserPersonalizado.objects.filter(telefone=telefone_limpo).exists():
            raise ValidationError("Este telefone já está cadastrado.")
        
        # 3. VALIDAÇÃO DE TAMANHO (Opcional, mas boa prática no form)
        if len(telefone_limpo) != 11:
             raise ValidationError("O telefone deve ter 11 dígitos (DDD + Número).")

        # 4. RETORNO: Devolve o telefone JÁ LIMPO.
        # Assim, o 'dicionario_limpo' na view já vai receber apenas números.
        return telefone_limpo

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
    


    '''
    
    Essa é a regra de ouro do Django:

    JavaScript (Frontend): É apenas "cosmético" (máscaras, avisos rápidos). Não serve para segurança.

    Models.py (Banco): É a última defesa (garante que o dado entre limpo no banco).

    Forms.py (O Porteiro Inteligente): É aqui que a mágica da validação acontece.

    O Problema que você estava tendo: Você limpava no Model, mas não no Form. O Form procurava (41) 9999...,
    o banco dizia "não tenho esse número (formatado)". O Form deixava passar. Aí o Model limpava para 419999...,
    tentava salvar, e o banco gritava "JÁ EXISTE!".
    
    
    
    '''