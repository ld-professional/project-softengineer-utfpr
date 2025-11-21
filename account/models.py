from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# tem q ter 2 classes auqi pq o django separa a lgoica de ciracao da logica de estrutura de dados
#  so precisamos criar a fabrica, o gerente, por causa do campo senha, em auth_user, difernete dos outros
#modelos, o quais ja vem com o gerente padrao do django...


#onde o trabalho eh simpels, o objects no caso.. ,receber os dados e salvar exatamente oq recebe
# basicamente como no meu docs, serve para fazer a criacao do objeto user, mas 
# n seria necessario, mas criamos um so pq temos q ter q fazer a senha apssar por uma hash de seguranca
# e logo tbm pdoeriamos n ter as validacoes aqui poderia ser feito pelo proprio forms.py mas
# aqui eh executado antes entao eh meio q devemos fazer as validacoes aqui tbm!

class CriadorUser(BaseUserManager):

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
            raise ValueError('O campo telefone é obrigatório.')
        
        # Normaliza o email (transforma letras maiúsculas em minúsculas no domínio)
        email = self.normalize_email(email)

        telefone_stringado= str(telefone) # n eh self.telefone pq telefone eh do objeto user e nao somos o user, e a
                                          # tbm a questao q ele entra ocmo arugmetno, auqi ja estamos pegando o self.telefone 
 
        #LIMPEZA
        # Remove tudo que não for dígito antes de salvar/validar 
        # precisa da validacao aqui se criar pelo cadastro,no forms esta sem... e se criar pelo admin o backends
        #  ta so para validar se existe e nao se esta correto..
        telefone_limpo = ''.join(filter(str.isdigit, str(telefone)))



        if len(telefone_limpo) != 11:
            raise ValueError({'telefone':'Digite um numero valido 43 91234 5678'})
        
        # 4. Criação do Objeto
        user = self.model(
            username=username,
            email=email,
            telefone=telefone_limpo,
        )

        # 5. Segurança da senha e Salvamento do objeto
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email,telefone, password=None):
        # O create_superuser precisa receber os argumentos que o create_user exige
        # O terminal vai pedir username, email e password. 

        
        if not telefone:
             raise ValueError('Superusuário precisa de telefone tambem.')
        
       
        telefone_limpo = ''.join(filter(str.isdigit, str(telefone)))

        if len(telefone_limpo) != 11:
            
            raise ValueError({'telefone':'Digite um numero valido 43 91234 5678'})

        user = self.create_user(
            username=username,
            email=email, 
            telefone=telefone,
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    

class UserPersonalizado(AbstractUser):
# Troquei para charfild para não perder o zero à esquerda (ex: 011...)
    telefone = models.CharField(max_length=11, unique=True) # campo q deve ser unico tbm sozinho obvio para este caso
    # apesar de ser nao aceitar nulo, nao impede de tentarem salvar None aqui, entao devemos fazer uma validacao
    # ou seja obviametne seria o forms.py mas n tem enfim sera no criador...

    # Configuração para o comando 'createsuperuser' no terminal
    # O 'username' já é o padrão do AbstractUser, então não precisa listar aqui.

    # Listamos apenas os CAMPOS EXTRAS que o terminal deve pedir.

    REQUIRED_FIELDS = ['email','username'] #'telefone'], LOGO como ja tem telefone para ser o principal, aqui deve ser email e username
    # lista de pgntas extras pro temrinal criar um superuser em: python manage.py createsuperuser

    USERNAME_FIELD = 'telefone' # na tela de login do /admin USAR telefone para login!

    def __str__(self):

        return f'User: {self.username}, email: {self.email}'
    

    # --- A CONEXÃO OBRIGATÓRIA ---
    # Diz ao modelo para usar o meu gerente/ fabrica q eh o craidorUser
    objects = CriadorUser() 


    #A Conexão: Ao escrever objects = CriadorUser(), você está dizendo:
    #  "Django, quando alguém chamar User.objects.create_user, não use o método padrão do Django.
    #  Use o método personalizado que EU escrevi na classe CriadorUser (aquele que verifica os 11 dígitos)."