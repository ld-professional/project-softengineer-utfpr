from django.contrib import admin
from .models import Cliente

# Register your models here.
class ClienteAdmin(admin.ModelAdmin):

    list_display=(
        'id_clientezao',
        'nome_cliente',
    )

    def nome_cliente(self,obj):
        return obj.fk_user.username
    
    search_fields=(
        'fk_user__username'
    )

admin.site.register(Cliente,ClienteAdmin)


# duvida:
# o self ja eh o proprio objeto como em python normal
# mas a questao eh q estamos no django e o obj ali como
# parametro
#
#- o self, eh a instancia da classe clienteadmin, e o obj
#-  eh a instancia do modelo cliente