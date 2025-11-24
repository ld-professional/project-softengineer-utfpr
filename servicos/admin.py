from django.contrib import admin
from .models import Servicos
# Register your models here.

class ServicosAdmin(admin.ModelAdmin):

    list_display=(

        'nome_servico',
        'preco_servico',
        "slot_duracao",
    )

    def slot_duracao(self,obj):
        duracao_em_string= obj.get_slot_duracao_servico_display()
        return duracao_em_string
    # na orpecisaria do metodo pq o django ao ver q o atributo
    # em lit dpslay tem chpocies, ele seria o get display visivel


    search_fields=(
        'nome_servico',
        #'slot_duracao_servico' pq aqui seria o inteiro 1 2 ou 3
        # pq o search fields eh comunicacao direta com o BD
        # logo para campos q tem lsit filtere vc deseja filtrar
        # para search, use list_filter um link clicavel
    )

    list_filter=([
        'slot_duracao_servico'
    ]
        #slot_duracao nao serveria assim como para o search field
    )


admin.site.register(Servicos,ServicosAdmin)