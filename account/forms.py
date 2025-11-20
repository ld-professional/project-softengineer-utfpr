#regra de ouro da segurança web é: "Nunca confie no Front-end".

# Validação no JS (Front-end): É para Experiência do Usuário (UX).

# Serve para dar feedback instantâneo ("Ei, as senhas não batem") sem precisar recarregar a página ou esperar o servidor.

from django import forms
from django.core.exceptions import ValidationError
from .models import UserCustomizado

class Forms_do_cadastro(forms.Form):
    ...
    