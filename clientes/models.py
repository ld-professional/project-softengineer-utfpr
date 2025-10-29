from django.db import models

# Create your models here.

class Cliente(models.Model):

    id_clientezao = models.AutoField(primary_key=True)
    