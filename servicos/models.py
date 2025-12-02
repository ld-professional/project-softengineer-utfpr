from django.db import models
from django.core.validators import MinValueValidator


duracoes= [
(1,'30 minutos'),
(2,'1 hora '),
(3,'1 hora e 30 minutos'),

]

regras= [
'nome_servico',
'preco_servico',
'slot_duracao_servico',
]

class Servicos(models.Model):

    id_servicos = models.AutoField(primary_key=True)

    nome_servico= models.CharField(max_length=25)
    preco_servico= models.DecimalField(max_digits=5,decimal_places=2,validators=[MinValueValidator(0)]) 
    
    slot_duracao_servico= models.IntegerField(choices=duracoes)

    def __str__(self):
        duracao= self.get_slot_duracao_servico_display()
        return f'Servico: {self.nome_servico}, preco: {self.preco_servico}, duracao:{duracao}'

    class Meta():
        constraints= [models.UniqueConstraint(name='servicos_constraint_unicos',fields=regras)]