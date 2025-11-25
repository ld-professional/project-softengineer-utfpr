from django.contrib.auth.backends import ModelBackend
from .loginstrategy import EmailStrategy, TelefoneStrategy,UsernameStrategy

from django.contrib.auth import get_user_model

class Contexto(ModelBackend):
    
   
    strategies = [
        EmailStrategy(),    
        TelefoneStrategy(), 
        UsernameStrategy(),
    ]                       

    def authenticate(self, request, username=None, password=None, **kwargs):
        
        UserPersonalizado= get_user_model()
        
        identifier = username 
        
        if identifier is None:
            identifier = kwargs.get(UserPersonalizado.USERNAME_FIELD)

        if identifier is None or password is None:
            return

        user=None

        user = self.buscar_usuario_nas_estrategias(identifier)

        if user and user.check_password(password) and self.user_can_authenticate(user):
                return user


    def buscar_usuario_nas_estrategias(self, identifier):
        """
        Percorre as estratégias, valida o formato e tenta buscar no banco.
        Retorna o User (se achar) ou None.
        """
        for strategy in self.strategies:
            
            if strategy.validar(identifier):
                
                return strategy.buscar_suposto_usuario(identifier)
        
        return None

