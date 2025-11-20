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

