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
 

        try:
            return User.objects.get(email__iexact=identifier)
        
        except User.DoesNotExist:
            return None


class TelefoneStrategy(LoginStrategyValidar):

    def validar(self, identifier):
        
        numeros = ''.join(filter(str.isdigit, identifier))

        
        
        return len(numeros) == 11
    

    def buscar_suposto_usuario(self, identifier):
        
        User = get_user_model()
        numeros = ''.join(filter(str.isdigit, identifier)) 
                                                            
        try:
            return User.objects.get(telefone=numeros)
        except User.DoesNotExist:
            return None
        

class UsernameStrategy(LoginStrategyValidar):

    def validar(self, identifier):

        if '@' in identifier:
            return False
        
        
        numeros = ''.join(filter(str.isdigit, identifier))
        if identifier.isdigit() and len(numeros) == 11:
            return False

        
        return True

    def buscar_suposto_usuario(self, identifier):
        User = get_user_model()
        try:
            
            return User.objects.get(username=identifier)
        except User.DoesNotExist:
            return None