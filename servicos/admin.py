from django.contrib import admin
from .models import Servicos


class ServicosAdmin(admin.ModelAdmin):

    list_display=(

        'nome_servico',
        'preco_servico',
        "slot_duracao",
    )

    def slot_duracao(self,obj):
        duracao_em_string= obj.get_slot_duracao_servico_display()
        return duracao_em_string
  
    search_fields=(
        'nome_servico',
       
    )

    list_filter=([
        'slot_duracao_servico'
    ]
    )


admin.site.register(Servicos,ServicosAdmin)