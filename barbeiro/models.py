from django.db import models
#from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
# Create your models here.
from django.conf import settings
from django.utils import timezone


# estes sao para a logica de edicao e salvamento de excecao
from django.apps import apps 
from django.utils import timezone
import datetime


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
        if not self.fk_barbeiro_id:
            erros['fk_barbeiro'] = "É obrigatório selecionar o barbeiro."
        if self.hora_inicio is None:
             erros['hora_inicio'] = "É obrigatório informar a hora de início."
        if self.hora_fim is None:
             erros['hora_fim'] = "É obrigatório informar a hora de término."
        if self.dia_semana is None:
             erros['dia_semana'] = "É obrigatório informar o dia da semana."

        if erros:
            raise ValidationError(erros)

        # 1. VALIDAÇÃO: FIM deve ser DEPOIS do INÍCIO
        if self.hora_inicio >= self.hora_fim:
            raise ValidationError({
                                    'hora_inicio': "A hora de término deve ser depois da hora de início."
                                })

        # 2. VALIDAÇÃO: CONFLITO DE HORÁRIO (Overlap entre turnos)
        conflitos = Horarios_de_trabalho.objects.filter(
            fk_barbeiro=self.fk_barbeiro_id,
            dia_semana=self.dia_semana,
            hora_fim__gt=self.hora_inicio,   
            hora_inicio__lt=self.hora_fim
        )
        if self.pk:
            conflitos = conflitos.exclude(pk=self.pk)

        if conflitos.exists():
            raise ValidationError(
                {'__all__': ['Conflito de horário! Já existe uma jornada de trabalho cadastrada neste intervalo para este barbeiro.']}
            )
        
        # 3. VALIDAÇÃO: VERIFICAR SE EDIÇÃO/DELETE AFETA AGENDAMENTOS FUTUROS
        
        Agendamentos = apps.get_model('agendamentos', 'Agendamentos') 
        
        # Mapeamento do dia da semana (0=Seg... 6=Dom) para o week_day do Django (1=Dom... 7=Sáb)
        dia_django = (self.dia_semana + 2) % 7 or 7 

        outros_turnos = Horarios_de_trabalho.objects.filter(
            fk_barbeiro=self.fk_barbeiro_id,
            dia_semana=self.dia_semana
        )
        if self.pk:
            outros_turnos = outros_turnos.exclude(pk=self.pk)

        intervalos_validos = [(self.hora_inicio, self.hora_fim)] 
        for turno in outros_turnos:
            intervalos_validos.append((turno.hora_inicio, turno.hora_fim))

        # Busca agendamentos futuros
        agendamentos_afetados = Agendamentos.objects.filter(
            fk_barbeiro=self.fk_barbeiro_id,
            data_e_horario_inicio__gte=timezone.localdate(), 
            data_e_horario_inicio__week_day=dia_django        
        )

        for ag in agendamentos_afetados:
            cabe = False

            # CORREÇÃO: Converte para o fuso local antes de extrair o time
            ag_inicio = ag.data_e_horario_inicio.astimezone(timezone.get_current_timezone()).time()
            ag_fim = ag.data_e_horario_fim.astimezone(timezone.get_current_timezone()).time()

            for inicio_trab, fim_trab in intervalos_validos: 
                if ag_inicio >= inicio_trab and ag_fim <= fim_trab:
                    cabe = True
                    break 
            
            if not cabe:
                 dia_str = ag.data_e_horario_inicio.strftime('%d/%m/%Y')
                 hora_str = ag.data_e_horario_inicio.strftime('%H:%M')

                 raise ValidationError(
                     {'__all__': [f"Ação bloqueada! O agendamento do cliente {ag.fk_cliente.fk_user.username} para {dia_str} às {hora_str} ficará sem horário de atendimento."]}
                 )
    





    # Removido *args e **kwargs para simplificar, já que não usamos multi-banco
    def delete(self):
        Agendamentos = apps.get_model('agendamentos', 'Agendamentos')
        mapa_dias = {0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 1}
        dia_django = mapa_dias.get(self.dia_semana)

        # Simula o dia SEM este horário
        outros_turnos = Horarios_de_trabalho.objects.filter(
            fk_barbeiro=self.fk_barbeiro_id, dia_semana=self.dia_semana
        ).exclude(pk=self.pk)
        
        intervalos_validos = []
        for turno in outros_turnos:
            intervalos_validos.append((turno.hora_inicio, turno.hora_fim))

        agendamentos = Agendamentos.objects.filter(
            fk_barbeiro=self.fk_barbeiro_id,
            data_e_horario_inicio__gte=datetime.date.today(),
            data_e_horario_inicio__week_day=dia_django
        )

        lista_de_conflitos_delete = [] # <--- Acumulador para o delete

        for ag in agendamentos:
            cabe = False
            ag_inicio = ag.data_e_horario_inicio.time()
            ag_fim = ag.data_e_horario_fim.time()

            for inicio_trab, fim_trab in intervalos_validos:
                if ag_inicio >= inicio_trab and ag_fim <= fim_trab:
                    cabe = True
                    break
            
            if not cabe:
                dia_str = ag.data_e_horario_inicio.strftime('%d/%m/%Y')
                hora_str = ag.data_e_horario_inicio.strftime('%H:%M')
                msg = f"Cliente {ag.fk_cliente.fk_user.username} ({dia_str} - {hora_str})"
                lista_de_conflitos_delete.append(msg)
        
        if lista_de_conflitos_delete:
            # Impede a deleção mostrando todos os afetados
            raise ValidationError(
                f"Não pode excluir! Agendamentos ficariam descobertos: {', '.join(lista_de_conflitos_delete)}"
            )
        
        # Chama o delete original sem argumentos
        super().delete()








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
  
        # Proteção de execução
        if not self.fk_barbeiro_id:
            esta_vazio_os_campos['fk_barbeiro'] = "É obrigatório selecionar o barbeiro."
        if not self.data_inicio:
            esta_vazio_os_campos['data_inicio'] = "É obrigatório informar a data de início."
        if not self.data_fim:
            esta_vazio_os_campos['data_fim'] = "É obrigatório informar a data de término."

        if esta_vazio_os_campos:
            raise ValidationError(esta_vazio_os_campos)

        # 1. Validação lógica: FIM deve ser DEPOIS do INÍCIO
        if self.data_inicio >= self.data_fim:
            raise ValidationError({'data_fim': "A data de término deve ser depois da data de início."})

        # 2. Validação: CONFLITO ENTRE EXCEÇÕES
        if self.fk_barbeiro_id:
            conflitos = Excecoes.objects.filter(
                fk_barbeiro_id=self.fk_barbeiro_id, 
                data_fim__gt=self.data_inicio,
                data_inicio__lt=self.data_fim
            )
            if self.pk:
                conflitos = conflitos.exclude(pk=self.pk)

            if conflitos.exists():
                raise ValidationError(
                    {'__all__': ['Conflito de horário! Já existe uma exceção cadastrada neste intervalo para este barbeiro.']}
                )
            
            # 3. Validação: CONFLITO COM AGENDAMENTOS EXISTENTES
            Agendamentos = apps.get_model('agendamentos', 'Agendamentos')
            
            agendamentos_conflitantes = Agendamentos.objects.filter(
                fk_barbeiro=self.fk_barbeiro_id,
                data_e_horario_inicio__lt=self.data_fim, 
                data_e_horario_fim__gt=self.data_inicio
            )
            
            lista_de_conflitos = []

            for ag in agendamentos_conflitantes:
                dia_str = ag.data_e_horario_inicio.strftime('%d/%m/%Y')
                hora_str = ag.data_e_horario_inicio.strftime('%H:%M')
                
                msg = f"Cliente {ag.fk_cliente.fk_user.username} ({dia_str} às {hora_str})"
                lista_de_conflitos.append(msg)
            
            if lista_de_conflitos:
                raise ValidationError(
                    {'__all__': [f"Não é possível adicionar esta indisponibilidade! Existem agendamentos marcados: {', '.join(lista_de_conflitos)}"]}
                )