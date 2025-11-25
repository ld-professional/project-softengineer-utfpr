from django.contrib import admin
from .models import Barbeiro, Horarios_de_trabalho, Excecoes

class BarbeiroAdmin(admin.ModelAdmin):

    list_display=(
        'nome_barbeiro',
        'email_barbeiro',
    )

    def email_barbeiro(self,obj):
        return obj.fk_user.email

    def nome_barbeiro(self,obj):
        return obj.fk_user.username
    
    search_fields=(
        'fk_user__username',
        'fk_user__email',
    )

    list_filter=([
        'fk_user', 
    ])

admin.site.register(Barbeiro,BarbeiroAdmin)

class Horarios_trabalhoAdmin(admin.ModelAdmin):

    list_display=(
        'barbeiro_nome',
        'dia_da_semana',
        'horario_de_inicio',
        'horario_final',
    )

    def horario_de_inicio(self,obj):
        return obj.hora_inicio
    
    def horario_final(self,obj):
        return obj.hora_fim

    def barbeiro_nome(self,obj):
        return obj.fk_barbeiro.fk_user.username

    def dia_da_semana(self,obj):
        return obj.get_dia_semana_display()
    

    search_fields=(
        'fk_barbeiro__fk_user__username',
        
    )

    list_filter=([
        'dia_semana',
        'fk_barbeiro',] 

    )

admin.site.register(Horarios_de_trabalho,Horarios_trabalhoAdmin)

class ExcecoesAdmin(admin.ModelAdmin):
    
    list_display=(
        'barbeiro_nome',
        'data_de_inicio',
        'data_de_fim',
    )

    def barbeiro_nome(self,obj):
        return obj.fk_barbeiro.fk_user.username
    
    def data_de_inicio(self,obj):
        return obj.data_inicio
    
    def data_de_fim(self,obj):
        return obj.data_fim
    
    search_fields=(
        'fk_barbeiro__fk_user__username',
        
    )

    list_filter=([
        'data_inicio', 
        'fk_barbeiro',
        'motivo_da_indisponibilidade',] 
    )

    
admin.site.register(Excecoes,ExcecoesAdmin)
