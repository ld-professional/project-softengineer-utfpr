from django.db import models

from clientes.models import Cliente
from barbeiro.models import Barbeiro,Excecoes,Horarios_de_trabalho
from servicos.models import Servicos
from django.core.exceptions import ValidationError
from datetime import timedelta

# Create your models here.
class Agendamentos(models.Model):

    id_agendamentos= models.AutoField(primary_key=True)

    fk_cliente= models.ForeignKey(Cliente,on_delete=models.CASCADE)
    fk_barbeiro = models.ForeignKey(Barbeiro,on_delete=models.CASCADE)
    fk_servicos= models.ForeignKey(Servicos,on_delete=models.CASCADE)
    data_e_horario_inicio = models.DateTimeField() # pode ser chamado de data + hora inicio
    data_e_horario_fim= models.DateTimeField(blank=True,null=True,editable=False) # sua logica/ salvamento eh feito no back end
                                                # usando data_fim= fk_serivcos_slot_duracao_servico *30
                                                # mas devo permitir o campo ser nulo a priori so pras primeiras
                                                #verificacoes de integridade de cada coluna nao falhas
                                                # pois de qlqer forma, na hora de salvar os dados no bd, ele salva todos
                                                # as colunas ao msm tempo, neste caso
                                                #editable eh um campo q so em view.py pode fazer adicioanr dado nesta ocluan
                                                # logo usuario em si, nem o admin cosnegue ver este campo
    class Meta:
        constraints=[models.UniqueConstraint(fields=[
            #'fk_cliente'                
            'fk_barbeiro',              # esta seria a pk pois num agendamento eh unico para cada linha o barbeiro + o exato momento
            'data_e_horario_inicio',    # mas o cliente tbm eh unico para cada data logo outra constraint
            ],
            name='agendamento_unico_por_barbeiro'
        ),
        models.UniqueConstraint(fields=[
            'fk_cliente',       
            #'fk_barbeiro',             
            'data_e_horario_inicio',   
            ],
            name='agendamento_unico_por_cliente',)
        ]

    def __str__(self):
        data_formatada = self.data_e_horario_inicio.strftime('%d/%m/%Y %H:%M')
    
    # para o caso de fazer qlqer coisa com o objeto antes msm dele ser asavlo no bd
        if self.data_e_horario_fim: 
            data_fim_formatada = self.data_e_horario_fim.strftime('%d/%m/%Y %H:%M')
            return f'''Cliente:{self.fk_cliente.fk_user.username}, com o barbeiro: {self.fk_barbeiro.fk_user.username},em:\n
                    {data_formatada} até {data_fim_formatada}.
                '''
    
        # se ele realmente ainda n foi salvo, logo usa este retorno
        return f'''Cliente:{self.fk_cliente.fk_user.username}, com o barbeiro: {self.fk_barbeiro.fk_user.username},em:\n
                {data_formatada} (calculando fim...)
        '''

    def clean(self):
    # lembrando q eh um metodo para validacao e nao salvamento... 
    # mei oq um meio termo sobre forms
    # ou seja, as variaveis vidnas do front atraves do json, serao passdas pra um forms
    # o qual tal forms salva cada variavel do json a uma acossaiada a um objeto do tipo agendamento
    # e no final chama este metodo clean
    # e dpeosi de chamar o clea, o useja o clean passar signfica q ta tudo ok
    # e se tiver tudo ok, ele entao salva no banco de dados
    # e dai no banc ode dados antes tbm por baixo dos panos faz as validacoes da class meta cosntraints ali...
        super().clean()

        # antes de tudo verificar se os campos n estao vazios, pois o def clean pode ser realizado pelo admins.py e a validacao fica
        # a cargo do backends.py porem roda antes o def clean e logo n passou pela validacao dos dados estarem vazios
    # 
    # O Django Admin (ou ModelForm) roda este método 'clean()' mesmo se
    # os campos obrigatórios estiverem vazios (None).
    # Se tentarmos acessar ou comparar 'None', o Python quebra com erro técnico.
    # Por isso, verificamos se temos os dados antes de rodar a lógica de negócio.
    #mas porque o Django insiste em rodar sua lógica mesmo quando os dados estão incompletos

    #mas ok se tem validacao proprai entao qual o sentido de ter auqi se o django
    #  ja roda antes o campo se eh null ou nao ? a questao eh q o django ele roda a
    #  validacao dele mas tbm o clean indepndente do restltuado se ta nulo ou nao ( msm q o bd o mdoels n permite null) 

        if not self.fk_cliente_id: # use _id pra caso se tiver realmetn nulo nao crashar a busca no bd 
            #raise ValidationError('preencha o campo do cliente')
            return # use return vazio pois pois se nao tera duplicacao de raise, o do q o django devolve de validacao e do clean
        if not self.fk_barbeiro_id:
            #raise ValidationError('preencha o campo do barbeiro')
            return
        if not self.fk_servicos_id:
            #raise ValidationError('preencha o campo do servicos')
            return
        if not self.data_e_horario_inicio:
            #raise ValidationError('preencha o campo do dia e horario')
            return

        #if not self.data_e_horario_fim:
            #pass  porque este aqui eh calculado no def clean






        duracao_em_minutos = self.fk_servicos.slot_duracao_servico * 30 
        inicio = self.data_e_horario_inicio
        fim = inicio + timedelta(minutes=duracao_em_minutos)
        self.data_e_horario_fim= fim

        conflitos =Agendamentos.objects.filter(
        fk_barbeiro=self.fk_barbeiro,
        data_e_horario_inicio__lt=self.data_e_horario_fim,
        data_e_horario_fim__gt= self.data_e_horario_inicio

        )
        if self.pk:
            conflitos = conflitos.exclude(pk=self.pk)
        
        if conflitos.exists():
            raise ValidationError(
                f'Conflito de horário! Ja existe um agendamento ocorrendo neste slot de horario!'
            )

        # conflitso q podem ocorrer ou eh se tem algumo horario, ou se o barbeiro nao trabalha em tal horario
        #ou se tem um excecao neste mesmo dia/horario de intervalo

        # para o intervalo de trabalho devemos chamar de conflito_nao_trabalha_em__tal_horario
        #
        # logo para descobrir lembrar q a models de horario_trabalho tem atributo dia, hora inicio e hora fim
        #
        #logo basta fazer dia_semana ( do banco de dados) ser == day(self.data_e_horarario_inicio)
        #
        # e para descobrir se o agendamento ocorre fora de um intervalo basta fazer se ele atende os requisitos de
        # estar dentro:
        # horario_inicio ( do banco) ser menor ou igual ao horario de inicio do agendamento 
        # horario final deve ser maior ou igual ao do agendamento
        #
        #ou seja lemrbando q pode ter N linhas pore xemplo 2 do msm dia, representando uma a tarde e outra demanha
        # logo
        # o retorno deve ser eralmetne q existe um intervalo neste dia
        #
        #logo chamar de barbeiro_trabalha_neste_intervalo= ..
        
        from barbeiro.models import Horarios_de_trabalho

        dia_para_agendar= (self.data_e_horario_inicio.weekday() + 1) % 7
                            # seria so weekday mas python considera segunda como zero entao some+1 e divide por 7
        hora_de_inicio= self.data_e_horario_inicio.time() #converte um DATETIME e m timefield
        hora_de_fim= self.data_e_horario_fim.time()




        barbeiro_trabalha_neste_intervalo= Horarios_de_trabalho.objects.filter(

                fk_barbeiro=self.fk_barbeiro,
                dia_semana= dia_para_agendar,
                hora_inicio__lte= hora_de_inicio, # este lte serve se hora_inicio eh menor ou igual a hora_de_inicio
                hora_fim__gte=hora_de_fim, # o gte eh se eh maior ou igual
        )
       
        if not barbeiro_trabalha_neste_intervalo.exists():
            raise ValidationError (f'barbeiro, {self.fk_barbeiro.fk_user.username} nao trabalha neste horario')
        


        from barbeiro.models import Excecoes

        existe_excecao_neste_intervalo= Excecoes.objects.filter(
            fk_barbeiro=self.fk_barbeiro,
            data_inicio__lt=self.data_e_horario_fim,
            data_fim__gt=self.data_e_horario_inicio,
        )

        if existe_excecao_neste_intervalo.exists():
            raise ValidationError (f'barbeiro, {self.fk_barbeiro.fk_user.username} nao consegue atender neste horario!')
