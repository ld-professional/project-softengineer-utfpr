from django.db import models
from django.contrib.auth.models import User
# Create your models here.



dias_da_semana = [
    (0, 'Domingo'),
    (1, 'Segunda'),
    (2, 'Terça'),
    (3, 'Quarta'),
    (4, 'Quinta'),
    (5, 'Sexta'),
    (6, 'Sábado'),
]

colunas_da_tabela_hora_trab=[
'fk_barbeiro',
'dia_semana',
'hora_inicio',
'hora_fim'
]

colunas_da_excecoes=[
#'fk_horario_de_trabalho__fk_barbeiro' 
# assim agora eu acessei a fk horario trab e entrei, e entao acessei o campo fk barbeiro e entrei, logo estou agr
# na tabela barbeiro, mas n pode, logo apenas referenciando a horario de trabalho, ja fica compreendido a unicidade
'fk_horario_de_trabalho',
'data_inicio',
'data_fim',
]




class Barbeiro(models.Model):

    id_barbeiro= models.AutoField(primary_key=True)
    #fk_user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=False)
    
    #ate poderia ser de vez settings.auth_user_model, ser User, mas aqui fica flexivel ja
    # e no caso sera msm pq eh mais facil e no padrao o djano n coloca esta linha no settings
    fk_user = models.OneToOneField(User,on_delete=models.CASCADE,null=False,related_name='barber')


class Horarios_de_trabalho(models.Model):

    id_horario_de_trabalho= models.AutoField(primary_key=True)
    fk_barbeiro= models.ForeignKey(Barbeiro,on_delete=models.CASCADE)
    dia_semana= models.IntegerField(choices=dias_da_semana)
    #Isso faz com que, no admin do Django, apareça um dropdown com os dias da semana em vez de números.
    hora_inicio= models.TimeField()
    hora_fim= models.TimeField()
    
    # agora a questao: hora inicio + hora fim + fk barbeiro deve ser UNIQUE logo...
    # logo devo criar uma subclasse Meta que representa um espaco para definir regras

    #ou seja as constraints de SQL e logo a variavel nesse espaco deve se chamar logo constraints
    # que recebe uma lsita das regras, no caso esta tabela horarios trabalho so tem 1
    class Meta():
        constraints= [models.UniqueConstraint(fields=colunas_da_tabela_hora_trab,name='unique_horario_barbeiro',name='unique_horario_barbeiro'), ]

        #logo esta classe guarda metadados ( nossas regras ) e nao dados...


class Excecoes(models.Model):

    id_excecoes= models.AutoField(primary_key=True)
    fk_horario_de_trabalho= models.ForeignKey(Horarios_de_trabalho,on_delete=models.CASCADE)
    
    data_inicio= models.DateTimeField()
    data_fim= models.DateTimeField()
    # ou seja supondo o front q ele seleciona o slot 9:30  10:00 10:30 e 11:00
    # logo data inicio sera dia tal vindo do front tb supondo 13/11 9:30 e dt fim 13/11 11:00
    class Meta():
        constraints= [models.UniqueConstraint(fields=colunas_da_excecoes,name='unique_horario_barbeiro') ,]