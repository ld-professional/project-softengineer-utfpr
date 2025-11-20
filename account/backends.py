# nao esquecer de adicionar no settings.py tal backends novo
#AUTHENTICATION_BACKENDS = [
#'django.contrib.auth.backends.ModelBackend',  # O backend padrão do Django (mantenha por seguranca e em segudna linha)
#    'account.backends.Contexto',    # Seu novo backend personalizado
#]


#A FUNÇÃO (MÉTODO) dentro dela DEVE se chamar authenticate
'''
O fluxo real é este:

    View: Chama authenticate(username=..., password=...).

        "Ei Django, tem alguém com esses dados? Não sei quem vai verificar, só me traga o usuário."

    Django (authenticate): Vai no settings.py.

        "Deixa eu ver quem está trabalhando hoje..."

        "Ah, o accounts.backends.Contexto é o primeiro da lista."

    Django: Instancia o seu Backend.

        backend = Contexto()

        user = backend.authenticate(...) (Aqui roda a sua lógica de Strategy).

    Seu Contexto:

        "Deixa comigo. Vou testar se é Email ou Telefone... Achei! Toma aqui o usuário."

    Django: Recebe o usuário e devolve para a View


'''


from django.contrib.auth.backends import ModelBackend
from .loginstrategy import EmailStrategy, TelefoneStrategy
#from .models import UserPersonalizado melhor usar o de baixo pq assim, da erro
#"o modelo chama o backend, o backend chama o modelo"
from django.contrib.auth import get_user_model

class Contexto(ModelBackend):
    
    ''' atuando como contexto de strategy pattern, vamos utilziar o arquivo loginstrategy e nao
        manter no msm arquivo o contexto o contrato e as implementacoes para fins visuais
        e basicamente relembrando>

        fluxo de cadastro eh receber json na views.py vindo do urls, enviar o json para o forms.py para validar
        se os dados estao coeretens e entao realiza o def clean das funcoes se necessario tambem para logica de insercao
        logo usar modelform e nao forms.form >> e por fim salvar o usuario

        fluxo de login: views.py recebe json com identifier e password, entrega o para o backends.py o qual
        fica resposnavel por validar os dados se estao corretametne digitados, e entao realizar a busca se tal usuario existe
        atraves do loginstrategy, que devolve ao backends.py o user em si, nao a linha ou o id, mas retorna a
          linha em objeto User
        ja, e entao com backends.py retorna ou none ou o user para a views.py
        a VIEWS.py entao se nao for nulo, for o user, envia tal user para os cookies do navegador e salva um dicionario
        com a url dashboard do cliente, e envia o json pro javascript e o javascript pega a chave 'url' e redireciona
          para este html
    '''

    # para realizar o backend eh simples tbm 1) copiar da origem  no modelbackend e copiando a funcao autenticate
    # 2) basta substituir os campos necessarios, por exemplo importar seu from .models import UserPersonalizado
    # e onde esta o User original trocar pelo Userpersonalziado...
    #e pra manter como um contexto ou seja temos q usar a logica de validacao dos campos pelo meu loginstrategy...
    # pode ver q eh bem o try/ except a funcao onde tenta realizar 

    strategies = [
         
        EmailStrategy(),    # todos os metodos tenho q instacialos aqui como variavel da classe e nao no init
        TelefoneStrategy(), # assim emailstrategy e telefone strategy sao da classe, e se um objeto fizer modificacao
    ]                       # ai ele modifica a variavel global

    '''
    Como suas estratégias (EmailStrategy, TelefoneStrategy) não guardam estado 
    (elas não têm self.valor ou self.usuario guardado dentro delas, apenas métodos de lógica),
    não faz sentido criar novas instâncias toda vez que alguém tenta logar.
    '''


    def authenticate(self, request, username=None, password=None, **kwargs):
        
        UserPersonalizado= get_user_model()
        
        identifier = username # Só para clareza

        # onde estes 2 if eh apenas se os campos nao sao nulos
        if identifier is None:
            identifier = kwargs.get(UserPersonalizado.USERNAME_FIELD)
            #esta linha veio da origem e mantem pq eh de seguranca

        if identifier is None or password is None:
            return
        

        user=None

        # Removemos o 'get_by_natural_key' (que é burro)
        # e colocamos o nosso Loop Inteligente.
        

        # 2. ABSTRAÇÃO: A busca complexa virou uma linha simples
        user = self.buscar_usuario_nas_estrategias(identifier)


        if user and user.check_password(password) and self.user_can_authenticate(user):
                return user
            




    def buscar_usuario_nas_estrategias(self, identifier):
        """
        Percorre as estratégias, valida o formato e tenta buscar no banco.
        Retorna o User (se achar) ou None.
        """
        for strategy in self.strategies:
            # Pergunta: O formato bate? (ex: é email?)
            if strategy.validar(identifier):
                # Ação: Busca no banco.
                # Se achou ou não, retornamos o resultado imediatamente.
                # (Não tentamos outras estratégias se o formato já bateu com uma).
                return strategy.buscar_suposto_usuario(identifier)
        
        return None

