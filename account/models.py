from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
# Create your models here.
# tem q ter 2 classes auqi pq o django separa a lgoica de ciracao da logica de estrutura de dados
#  so precisamos criar a fabrica, o gerente, por causa do campo senha, em auth_user, difernete dos outros
#modelos, o quais ja vem com o gerente padrao do django...


#onde o trabalho eh simpels, o objects no caso.. ,receber os dados e salvar exatamente oq recebe

class criador_user(BaseUserManager):

    def create_user(self,username,email,telefone,password=None):

        """
        Cria e salva um Usuário comum.
        Obrigatório: email, username, cpf e senha.
        """

        if not email:
            raise ValueError('O campo Email é obrigatório.')
        if not username:
            raise ValueError('O campo Username é obrigatório.')
        if not telefone:
            raise ValueError('O campo CPF é obrigatório.')
        
        # Normaliza o email (transforma letras maiúsculas em minúsculas no domínio)
        email = self.normalize_email(email)

        telefone_stringado= str(self.telefone)

        if telefone_stringado.count() >11
            raise ValueError({'telefone':'O campo telefone necessita ser de 11 digitos'})