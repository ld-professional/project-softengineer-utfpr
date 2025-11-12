from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Cliente(models.Model):
    id_clientezao = models.AutoField(primary_key=True)
    fk_user= models.OneToOneField(User,on_delete=models.CASCADE,related_name='clientao')
    
    class Meta():

        constraints=[models.UniqueConstraint(name='cliente_user_unico',fields=['id_clientezao','fk_user'])]

    def __str__(self):
        return f"Cliente: {self.fk_user.username}"