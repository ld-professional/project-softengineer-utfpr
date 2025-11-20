from abc import ABC, abstractmethod


class LoginStrategyValidar(ABC):

    @abstractmethod 
    def validar(self,identifier):
        """Retorna True se o formato parece correto (ex: é um email?)."""
        pass

    @abstractmethod 
    def buscar_suposto_usuario(self,identifier):
        """Busca no banco e retorna o User ou None."""
        pass



from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class EmailStrategy(LoginStrategyValidar):

    def validar(self, identifier):
        
        try:
            validate_email(identifier)         
            return True
        
        except ValidationError:
            return False
        

    def buscar_suposto_usuario(self, identifier):

        User = get_user_model()
 #o get_user_model(), Ela vai no seu arquivo settings.py.
#Ela lê a configuração AUTH_USER_MODEL.
#Ela descobre qual classe você definiu lá (no seu caso, accounts.UserPersonalizado).
#Ela nao instancia  essa classe lee sera a propria classe e coloca a dentro da variável User.
# logo user.objects ( definidio em models.py eh igual a  criado_user() ou seja eh uma instancia dele e 
# #chamamos o metodo get  definido nele
# este metodo get herdado, e nao eu q escrevi, procura no banco de dados, o parametro q vc passar
# no caso como nossa coluna deuser tem um campo chamado email, o django criou para todas as colunas uma
# forma de comparar os resultado, adicionado <nome_coluna>__iexact = identifier
# assim levamos para a variavel email__iexact o valor identifier, onde ele vai comparar se no BD tem alguma
# linha com este valor, se sim, como eh metodo get, nos retorna esta linha, no caso o User em si ( nao o id)

        try:
            return User.objects.get(email__iexact=identifier)
        
        except User.DoesNotExist:
            return None


class TelefoneStrategy(LoginStrategyValidar):

    def validar(self, identifier):
        # Limpa e deixa só números
        numeros = ''.join(filter(str.isdigit, identifier))

        # 1) str.isdigit: se n for algum caracter entre 0 e 9 retorna false, ele eh um juiz do lado esqeurdo
        # diz se tal caracter eh true ( continua) ou false ( sai da palavra)
        # 43 99900-1330 => ['4', '3', '9', '9', '9', '0', '0','1', '3', '3', '0', '0']
        # o Join pega a lista e junta numa string, onde entre cara carater tem '' ou seja nenhum espaco


        # Regra: 11 digitos
        return len(numeros) == 11
    

    def buscar_suposto_usuario(self, identifier):
        
        User = get_user_model()
        numeros = ''.join(filter(str.isdigit, identifier)) # refiz aqui pq a string eh suja e na funcao
                                                            # de cima n retorna ela, mas bool
        try:
            return User.objects.get(telefone=numeros)
        except User.DoesNotExist:
            return None
        

