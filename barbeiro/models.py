from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class barbeiro(models.Model):

    id_barbeiro= models.AutoField(primary_key=True)
    fk_user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=False)
    
    #ate poderia ser de vez settings.auth_user_model, ser User, mas aqui fica flexivel ja

class horarios_de_trabalho(models.Model):

    id_horario_de_trabalho= models.AutoField(primary_key=True)
    fk_barbeiro= models.ForeignKey(barbeiro,on_delete=models.CASCADE)

