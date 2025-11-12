from django.db import models

# Create your models here.

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

    nome_servico= models.CharField(max_length=100)
    preco_servico= models.PositiveIntegerField()
    slot_duracao_servico= models.IntegerField(choices=duracoes)

    def __str__(self):
        duracao= self.get_slot_duracao_servico_display()
        return f'Servico: {self.nome_servico}, preco: {self.preco_servico}, duracao:{duracao}'

    class Meta():
        constraints= [models.UniqueConstraint(name='servicos_constraint_unicos',fields=regras)]



#a duracoes por exemplo faz so existir uma destas 3 opcoes, e o seguinte:
#
# no html por exemplo aparece o 30 minutos ou 1hr ou 1hr e 30 para selecionar
#
# entao supondo selecionado 30 minutos, sera covnertido para o numero itneger 1

#
#em vez do número, usa o método automático que o Django cria pra cada campo com choices:
#Servicos.get_slot_duracao_servico_display()

#>>> servico = Servicos.objects.get(id_servicos=1)
#>>> servico.slot_duracao_servico
#1
#>>> servico.get_slot_duracao_servico_display()
#'30 minutos'