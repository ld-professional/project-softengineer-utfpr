from django.db import models

from clientes.models import Cliente
from barbeiro.models import Barbeiro,Excecoes,Horarios_de_trabalho
from servicos.models import Servicos
from django.core.exceptions import ValidationError
from datetime import timedelta

# Create your models here.
class Agendamentos(models.Model):

    id_agendamentos= models.AutoField(primary_key=True)

    fk_cliente= models.ForeignKey(Cliente,on_delete=models.CASCADE)
    fk_barbeiro = models.ForeignKey(Barbeiro,on_delete=models.CASCADE)
    fk_servicos= models.ForeignKey(Servicos,on_delete=models.CASCADE)
    data_e_horario_inicio = models.DateTimeField() # pode ser chamado de data + hora inicio
    data_e_horario_fim= models.DateTimeField(blank=True,null=True,editable=False) # sua logica/ salvamento eh feito no back end
                                                # usando data_fim= fk_serivcos_slot_duracao_servico *30
                                                # mas devo permitir o campo ser nulo a priori so pras primeiras
                                                #verificacoes de integridade de cada coluna nao falhas
                                                # pois de qlqer forma, na hora de salvar os dados no bd, ele salva todos
                                                # as colunas ao msm tempo, neste caso
                                                #editable eh um campo q so em view.py pode fazer adicioanr dado nesta ocluan
                                                # logo usuario em si, nem o admin cosnegue ver este campo
    class Meta:
        constraints=[models.UniqueConstraint(fields=[
            #'fk_cliente'                
            'fk_barbeiro',              # esta seria a pk pois num agendamento eh unico para cada linha o barbeiro + o exato momento
            'data_e_horario_inicio',    # mas o cliente tbm eh unico para cada data logo outra constraint
            ],
            name='agendamento_unico_por_barbeiro'
        ),
        models.UniqueConstraint(fields=[
            'fk_cliente',       
            #'fk_barbeiro',             
            'data_e_horario_inicio',   
            ],
            name='agendamento_unico_por_cliente',)
        ]

    def __str__(self):
        data_formatada = self.data_e_horario_inicio.strftime('%d/%m/%Y %H:%M')
    
    # para o caso de fazer qlqer coisa com o objeto antes msm dele ser asavlo no bd
        if self.data_e_horario_fim: 
            data_fim_formatada = self.data_e_horario_fim.strftime('%d/%m/%Y %H:%M')
            return f'''Cliente:{self.fk_cliente.fk_user.username}, com o barbeiro: {self.fk_barbeiro.fk_user.username},em:\n
                    {data_formatada} até {data_fim_formatada}.
                '''
    
        # se ele realmente ainda n foi salvo, logo usa este retorno
        return f'''Cliente:{self.fk_cliente.fk_user.username}, com o barbeiro: {self.fk_barbeiro.fk_user.username},em:\n
                {data_formatada} (calculando fim...)
        '''

    def clean(self):
    # lembrando q eh um metodo para validacao e nao salvamento... 
    # mei oq um meio termo sobre forms
    # ou seja, as variaveis vidnas do front atraves do json, serao passdas pra um forms
    # o qual tal forms salva cada variavel do json a uma acossaiada a um objeto do tipo agendamento
    # e no final chama este metodo clean
    # e dpeosi de chamar o clea, o useja o clean passar signfica q ta tudo ok
    # e se tiver tudo ok, ele entao salva no banco de dados
    # e dai no banc ode dados antes tbm por baixo dos panos faz as validacoes da class meta cosntraints ali...
        super().clean()

        duracao_em_minutos = self.fk_servicos.slot_duracao_servico * 30 
        inicio = self.data_e_horario_inicio
        fim = inicio + timedelta(minutes=duracao_em_minutos)
        self.data_e_horario_fim= fim

        conflitos =Agendamentos.objects.filter(
        fk_barbeiro=self.fk_barbeiro,
        data_e_horario_inicio__lt=self.data_e_horario_fim,
        data_e_horario_fim__gt= self.data_e_horario_inicio

        )
        if self.pk:
            conflitos = conflitos.exclude(pk=self.pk)
        
        if conflitos.exists():
            raise ValidationError(
                f'Conflito de horário! Ja existe um agendamento ocorrendo neste slot de horario!'
            )

        # ainda falta toda logica do agendamento mas isso sera feito como parte do bac-end para agendamentos...