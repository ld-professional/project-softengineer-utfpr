from django import forms
from .models import Horarios_de_trabalho, dias_da_semana

class HorariosTrabalhoMultiDiaForm(forms.ModelForm):

    dias = forms.MultipleChoiceField(
        choices=dias_da_semana,        
        widget=forms.CheckboxSelectMultiple, 
        required=True, 
        label="Dias da semana (Selecione um ou mais)"
    )

    class Meta:
        model = Horarios_de_trabalho
        
        fields = ['fk_barbeiro', 'dias', 'hora_inicio', 'hora_fim']
       

    def _post_clean(self):
        """
        Sobrescrevemos este método para IMPEDIR que o Django tente validar 
        a instância do Model agora. Como o campo 'dia_semana' não existe 
        neste form, a validação padrão quebraria o código.
        Deixaremos para validar manualmente no admin.py, dia por dia.
        """
        pass









from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class EditarPerfilBarbeiroForm(forms.ModelForm):
    foto_barbeiro = forms.ImageField(required=False)
    
    # Senha atual obrigatória na validação lógica
    senha_atual = forms.CharField(
        required=False, # Deixamos False aqui para tratar a mensagem no clean()
        widget=forms.PasswordInput
    )
    nova_senha = forms.CharField(
        required=False, 
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'telefone']

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        telefone_limpo = ''.join(filter(str.isdigit, str(telefone)))
        
        if len(telefone_limpo) != 11:
            raise ValidationError("O telefone deve ter exatamente 11 dígitos.")
        
        if User.objects.filter(telefone=telefone_limpo).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este telefone já está em uso.")

        return telefone_limpo

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este nome de usuário já está em uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        senha_atual = cleaned_data.get('senha_atual')
        nova_senha = cleaned_data.get('nova_senha')

        # REGRA RIGIDA: Senha Atual é OBRIGATÓRIA para qualquer coisa
        if not senha_atual:
            self.add_error('senha_atual', "Digite sua senha atual para salvar as alterações.")
        else:
            # Se digitou, verifica se está certa
            if not self.instance.check_password(senha_atual):
                self.add_error('senha_atual', "A senha atual está incorreta.")

        # Validação da nova senha (apenas se digitou algo nela)
        if nova_senha:
            if len(nova_senha) < 8:
                self.add_error('nova_senha', "A nova senha deve ter no mínimo 8 caracteres.")

        return cleaned_data