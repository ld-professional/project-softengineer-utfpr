from django.contrib import admin
from .models import Agendamentos
# Register your models here.

#ADMIN SERVE APENAS para questao de manutenabilidade
# e se algm quiser alguma troca de email por exemplo
# um cliente ou qlqer edicao de algum objeto criado,
# basta acessar este painel feito do django admin
# e entaoeu consigo editar


class AgendamentosAdmin(admin.ModelAdmin):
    list_display = (
        'cliente_nome',
        'barbeiro_nome',
        'servico_nome',
        'servico_preco',
        'data_e_horario_inicio',
        'data_e_horario_fim'
    )

    # Métodos para acessar campos relacionados:

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
   # É um atributo do método, não do preço,
   #  nem do serviço.
    #
   # Quando este método aparecer na lista do admin,
   #  use 'Preço' como título da coluna.
   #
   # você configura um atributo especial usado apenas para o Admin 
   # esse atributo personaliza o nome da coluna


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