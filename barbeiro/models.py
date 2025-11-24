from django.db import models
#from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
# Create your models here.
from django.conf import settings



dias_da_semana = [
    (0, 'Segunda'),
    (1, 'Terça'),
    (2, 'Quarta'),
    (3, 'Quinta'),
    (4, 'Sexta'),
    (5, 'Sábado'),
    (6, 'Domingo'),
]

colunas_da_tabela_hora_trab=[
'fk_barbeiro',
'dia_semana',
'hora_inicio',
#'hora_fim' assim permite apenas q n tenham horarios q coemcem no msm
]

colunas_da_excecoes=[
#'fk_horario_de_trabalho__fk_barbeiro' 
# assim agora eu acessei a fk horario trab e entrei, e entao acessei o campo fk barbeiro e entrei, logo estou agr
# na tabela barbeiro, mas n pode, logo apenas referenciando a horario de trabalho, ja fica compreendido a unicidade
'fk_barbeiro',
'data_inicio',
# 'data_fim', assim permite q n pode ter excecoes q estejam no msm comeco

]
# pensando melhor mer para modelo fisico usar direto fk_barbeiro ja que estas 2 entidades so definem a regra
#no mer faz ate sentido usar elas depnedneo uma da outra, mas auqi o melhor caminho nao eh estarem ligadas
# pois o excecoes so usa a tabela de horario de trabalho pra acessar o barbeiro...



class Barbeiro(models.Model):

    id_barbeiro= models.AutoField(primary_key=True)
    #fk_user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=False)
    
    #ate poderia ser de vez settings.auth_user_model, ser User, mas aqui fica flexivel ja
    # e no caso sera msm pq eh mais facil e no padrao o djano n coloca esta linha no settings
    fk_user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=False,related_name='barber')
    foto_barbeiro= models.ImageField(
    upload_to='fotos_barbeiros/',
    null=True,
    blank=True,
    )

    class Meta():

        constraints=[models.UniqueConstraint(name='barbeiro_user_unico',fields=['id_barbeiro','fk_user'])]

    def __str__(self):
        return f'Barbeiro:{self.fk_user.username}'

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
        constraints= [models.UniqueConstraint(fields=colunas_da_tabela_hora_trab,name='unique_horario_barbeiro',), ]

        #logo esta classe guarda metadados ( nossas regras ) e nao dados...

    def __str__(self):
        dia_da_semana_string= dict(dias_da_semana).get(self.dia_semana,'Desconhecido')
        return f'Horario de trabalho do barbeiro: {self.fk_barbeiro.fk_user.username}:\nDia da semana {dia_da_semana_string}, {self.hora_inicio} : {self.hora_fim} '
        # para navegar nao pelo ORM que eh __, aqui eh por ponto normal como python
        #dict transforma a nossa lista de tupla em dicionario
        #get tenta buscar pela chave self.dia_semana e o resultado salva em dia da semana string
        #se nao achar, o conteudo sera o "desconhecido"

    def clean(self):
        super().clean()
        
        erros = {}

        # PROTEÇÃO DE EXECUÇÃO (Verifica IDs e campos nulos)
        # Usamos fk_barbeiro_id para não tentar buscar o objeto se o campo estiver vazio
        if not self.fk_barbeiro_id:
            erros['fk_barbeiro'] = "É obrigatório selecionar o barbeiro."
        
        # Verifica se os horários foram preenchidos (TimeField pode ser None se o form estiver vazio)
        if self.hora_inicio is None:
             erros['hora_inicio'] = "É obrigatório informar a hora de início."
        
        if self.hora_fim is None:
             erros['hora_fim'] = "É obrigatório informar a hora de término."
             
        if self.dia_semana is None:
             erros['dia_semana'] = "É obrigatório informar o dia da semana."

        # Se faltou algo básico, para aqui e mostra os erros
        if erros:
            raise ValidationError(erros)


        if self.hora_inicio and self.hora_fim:
            if self.hora_inicio >= self.hora_fim:
                raise ValidationError({
                                    'hora_inicio': "A hora de término deve ser depois da hora de início."
                                        })

        conflitos = Horarios_de_trabalho.objects.filter(
            fk_barbeiro=self.fk_barbeiro_id,
            dia_semana=self.dia_semana,
            hora_fim__gt=self.hora_inicio,   
            hora_inicio__lt=self.hora_fim
        )

        if self.pk:
            conflitos = conflitos.exclude(pk=self.pk)

        if conflitos.exists():
            raise ValidationError('Conflito de horário! Já existe uma exceção cadastrada neste intervalo para este barbeiro.')


class Excecoes(models.Model):

    id_excecoes= models.AutoField(primary_key=True)
    fk_barbeiro= models.ForeignKey(Barbeiro,on_delete=models.CASCADE)
    
    data_inicio= models.DateTimeField()
    data_fim=models.DateTimeField()
    motivo_da_indisponibilidade= models.CharField(null=True,max_length=200)
    # ou seja supondo o front q ele seleciona o slot 9:30  10:00 10:30 e 11:00
    # logo data inicio sera dia tal vindo do front tb supondo 13/11 9:30 e dt fim 13/11 11:00
    class Meta():
        constraints= [models.UniqueConstraint(fields=colunas_da_excecoes,name='unique_excecao') ,]

    def __str__(self):
       
     return f'Horario indisponivel de: {self.fk_barbeiro.fk_user.username}:\n {self.data_inicio} até {self.data_fim} '
    
    def clean(self):
        super().clean()

        esta_vazio_os_campos = {}
  
        #Isso não é bem uma "validação" (tipo dizer "é proibido ser vazio"), é mais uma proteção de execução. 
        # Você está dizendo: "Só rode a lógica pesada de verificar conflitos no banco
        #  SE eu tiver os dados básicos na mão".

        if not self.fk_barbeiro_id:
            esta_vazio_os_campos['fk_barbeiro'] = "É obrigatório selecionar o barbeiro."
            
        if not self.data_inicio:
            esta_vazio_os_campos['data_inicio'] = "É obrigatório informar a data de início."
        if not self.data_fim:
            esta_vazio_os_campos['data_fim'] = "É obrigatório informar a data de término."

        if esta_vazio_os_campos:
            raise ValidationError(esta_vazio_os_campos)

        # Validação lógica
        if self.data_inicio >= self.data_fim:
            raise ValidationError({'data_fim': "A data de término deve ser depois da data de início."})

        # Verifica conflitos (Somente se o barbeiro existe)
        if self.fk_barbeiro_id:
            conflitos = Excecoes.objects.filter(
                fk_barbeiro_id=self.fk_barbeiro_id, # Usa o ID
                data_fim__gt=self.data_inicio,
                data_inicio__lt=self.data_fim
            )
            if self.pk:
                conflitos = conflitos.exclude(pk=self.pk)

            if conflitos.exists():
                raise ValidationError(
                    'Conflito de horário! Já existe uma exceção cadastrada neste intervalo para este barbeiro.'
                )