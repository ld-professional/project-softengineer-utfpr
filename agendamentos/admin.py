from django.contrib import admin
from .models import Agendamentos


class AgendamentosAdmin(admin.ModelAdmin):
    list_display = (
        'cliente_nome',
        'barbeiro_nome',
        'servico_nome',
        'servico_preco',
        'data_e_horario_inicio',
        'data_e_horario_fim',
    )


    def cliente_nome(self, obj):
        return obj.fk_cliente.fk_user.username
    cliente_nome.short_description = 'Cliente'

    def barbeiro_nome(self, obj):
        return obj.fk_barbeiro.fk_user.username
    barbeiro_nome.short_description = 'Barbeiro'

    def servico_nome(self, obj):
        return obj.fk_servicos.nome_servico
    servico_nome.short_description = 'Serviço'

    def servico_preco(self, obj):
        return obj.fk_servicos.preco_servico
    servico_preco.short_description = 'Preço'
   

    search_fields = (

        'fk_cliente__fk_user__username',
        'fk_barbeiro__fk_user__username',
        'fk_servicos__nome_servico',

    )

    list_filter=(
        
        'data_e_horario_inicio',
        'fk_barbeiro',
        'fk_cliente',
        
    )

admin.site.register(Agendamentos,AgendamentosAdmin)