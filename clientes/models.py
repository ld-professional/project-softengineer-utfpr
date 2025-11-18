from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from django.core.exceptions import ValidationError


class Cliente(models.Model):
    id_clientezao = models.AutoField(primary_key=True)
    fk_user= models.OneToOneField(User,on_delete=models.CASCADE,related_name='clientao')
    
    class Meta():

        constraints=[models.UniqueConstraint(name='cliente_user_unico',fields=['id_clientezao','fk_user'])]

    def __str__(self):
        return f"Cliente: {self.fk_user.username}"
    
    def clean(self):

        super().clean()

        if not self.fk_user_id:
            raise ValidationError({'fk_user':'Campo obrigatorio!'})
        
        #Ao adicionar _id ao nome do campo, você verifica apenas se o número do ID está preenchido na memória,
        #  sem tentar buscar o usuário inteiro no banco de dados (o que causava o erro).