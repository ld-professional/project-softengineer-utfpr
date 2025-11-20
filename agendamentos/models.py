from django.db import models

from clientes.models import Cliente
from barbeiro.models import Barbeiro,Excecoes,Horarios_de_trabalho
from servicos.models import Servicos
from django.core.exceptions import ValidationError
from datetime import timedelta

class Agendamentos(models.Model):

    id_agendamentos= models.AutoField(primary_key=True)

    fk_cliente= models.ForeignKey(Cliente,on_delete=models.CASCADE)
    fk_barbeiro = models.ForeignKey(Barbeiro,on_delete=models.CASCADE)
    fk_servicos= models.ForeignKey(Servicos,on_delete=models.CASCADE)
    data_e_horario_inicio = models.DateTimeField()
    data_e_horario_fim= models.DateTimeField(blank=True,null=True,editable=False)
    class Meta:
        constraints=[models.UniqueConstraint(fields=[
            'fk_barbeiro',
            'data_e_horario_inicio'],
            name='agendamento_unico_por_barbeiro'),

        models.UniqueConstraint(fields=[
            'fk_cliente',       
            'data_e_horario_inicio'],
            name='agendamento_unico_por_cliente',)
        ]

    def __str__(self):
        data_formatada = self.data_e_horario_inicio.strftime('%d/%m/%Y %H:%M')
    
        if self.data_e_horario_fim: 
            data_fim_formatada = self.data_e_horario_fim.strftime('%d/%m/%Y %H:%M')
            return f'''Cliente:{self.fk_cliente.fk_user.username}, com o barbeiro: {self.fk_barbeiro.fk_user.username},em:\n
                    {data_formatada} até {data_fim_formatada}.
                '''
    
        return f'''Cliente:{self.fk_cliente.fk_user.username}, com o barbeiro: {self.fk_barbeiro.fk_user.username},em:\n
                {data_formatada} (calculando fim...)
        '''

    def clean(self):
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
            raise ValidationError(f'Conflito de horário! Ja existe um agendamento ocorrendo neste slot de horario!')