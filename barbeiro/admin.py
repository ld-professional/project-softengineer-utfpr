from django.contrib import admin
from .models import Barbeiro, Horarios_de_trabalho, Excecoes,dias_da_semana

from .forms import HorariosTrabalhoMultiDiaForm # Importe o form que criamos

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
    


    form = HorariosTrabalhoMultiDiaForm  # <-- usa o formulário customizado

# === AQUI ESTÁ O SEGREDO DO SAVE_MODEL ===
    def save_model(self, request, obj, form, change):
        dias_selecionados = form.cleaned_data['dias']
        barbeiro = form.cleaned_data['fk_barbeiro']
        h_inicio = form.cleaned_data['hora_inicio']
        h_fim = form.cleaned_data['hora_fim']

        for dia_codigo in dias_selecionados:
            # Cria o objeto na memória
            novo_horario = Horarios_de_trabalho(
                fk_barbeiro=barbeiro,
                dia_semana=int(dia_codigo), # Converte '0' para 0
                hora_inicio=h_inicio,
                hora_fim=h_fim
            )
            
            # criamos o objeto com o dia tal, e horario inico e horario fim q ja temos, vindo do form...
            # e entao tentamos salvar ele, mas antes rodar agora o full clean deste objeto
            #  q eh um models/horario_de_trabalho
            try:
                novo_horario.full_clean() # primeiro testar o clean se a logica de insercao ta ok
                novo_horario.save()       # pois apesar de ser model.forms, retiramos o clean de la e entao save
            except Exception as e:
                # Opcional: Se quiser que o erro apareça de forma amigável no topo da página
                from django.contrib import messages
                dia_nome = dict(dias_da_semana).get(int(dia_codigo))
                messages.error(request, f"Erro ao salvar {dia_nome}: {e}")
                # Se quiser parar tudo no primeiro erro, descomente a linha abaixo:
                # return 

                # 2. TRUQUE PARA EVITAR O ERRO RelatedObjectDoesNotExist
        # O Django precisa imprimir esse objeto para o Log de Histórico.
        # Vamos preencher ele com os dados do form só para o __str__ funcionar.
        obj.fk_barbeiro = barbeiro
        obj.dia_semana = int(dias_selecionados[0]) # Pega o primeiro dia escolhido
        obj.hora_inicio = h_inicio
        obj.hora_fim = h_fim

        # 3. Importante: NÃO salvamos o 'obj' (não chamamos super), 
        # pois ele é apenas o fantoche do formulário.
         # Não chamamos super().save_model()
        return

       


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
