from django.contrib import admin
from .models import Cliente

class ClienteAdmin(admin.ModelAdmin):

    list_display=(
        'id_clientezao',
        'nome_cliente',
    )

    def nome_cliente(self,obj):
        return obj.fk_user.username
    
    search_fields=(
        ['fk_user__username']
    )

admin.site.register(Cliente,ClienteAdmin)