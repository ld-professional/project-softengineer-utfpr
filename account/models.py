from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CriadorUser(BaseUserManager):

    def create_user(self,username,email,telefone,password=None):



        if not email:
            raise ValueError('O campo Email é obrigatório.')
        if not username:
            raise ValueError('O campo Username é obrigatório.')
        if not telefone:
            raise ValueError('O campo telefone é obrigatório.')
        

        email = self.normalize_email(email)

        telefone_stringado= str(telefone) 
        telefone_limpo = ''.join(filter(str.isdigit, str(telefone)))



        if len(telefone_limpo) != 11:
            raise ValueError({'telefone':'Digite um numero valido 43 91234 5678'})
        
        user = self.model(
            username=username,
            email=email,
            telefone=telefone_limpo,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email,telefone, password=None):

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
    


from django.core.validators import RegexValidator # ai precisa deste import para sobresscrever user

class UserPersonalizado(AbstractUser):

    '''
     agora quer sobrescrever username logo so ir na definicao copiar oq tem la, e copiar o validador tbm, e sobrescrever 
     o validador q eh onde n permite espacos...
    -> basta apenas copiar e colar da definicao  e onde ta regex, dar um espaco dentro da aspas simples...
    
    # obs: se n quiser permitir numeros no username, trouqe \w por: regex=r'^[a-zA-Z_.@+\- ]+$',
    '''

    validador_com_espaco = RegexValidator(
        regex=r'^[a-zA-Z_.@+\- ]+$', # coloque uma barra invertida antes do hifen se n ele acha q eh intervalo este espaco
        message='O nome de usuário pode conter letras, números, ESPAÇOS e caracteres @/./+/-/_',
        flags=0
    )


    username = models.CharField(
        'username',
        max_length=33,
        unique=True,
        help_text='Obrigatório. 150 caracteres ou menos. Letras, dígitos, espaços e @/./+/-/_ apenas.',
        validators=[validador_com_espaco], # <--- Usamos o nosso aqui
        error_messages={
            'unique': "Um usuário com este nome já existe.",
        },
    )


    telefone = models.CharField(max_length=11, unique=True) 

    REQUIRED_FIELDS = ['email','telefone',] 

    USERNAME_FIELD = 'username' 

    def __str__(self):

        return f'User: {self.username}, email: {self.email}'
    

    objects = CriadorUser() 
