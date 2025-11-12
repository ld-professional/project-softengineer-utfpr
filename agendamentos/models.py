from django.db import models

from clientes.models import Cliente
from barbeiro.models import Barbeiro,Excecoes,Horarios_de_trabalho
from servicos.models import Servicos

# Create your models here.
class Agendamentos(models.Model):

    id_agendamentos= models.AutoField(primary_key=True)

    fk_cliente= models.ForeignKey(Cliente,on_delete=models.CASCADE)
    fk_barbeiro = models.ForeignKey(Barbeiro,on_delete=models.CASCADE)
    fk_servicos= models.ForeignKey(Servicos,on_delete=models.CASCADE)
    data_e_horario = models.DateTimeField()

    class Meta:
        constraints=[models.UniqueConstraint(fields=[
            'fk_cliente',
            'fk_barbeiro',
            'fk_servicos',
            'data_e_horario',],
            name='agendamento_unico'
        )]

    def __str__(self):
        data_formatada = self.data_e_horario.strftime('%d/%m/%Y %H:%M')
        return f'''Cliente:{self.fk_cliente.fk_user.username}, com o barbeiro: {self.fk_barbeiro.fk_user.username},em:\n
                    {data_formatada}.
        '''