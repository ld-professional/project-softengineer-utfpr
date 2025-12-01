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
    # Campos EXTRAS (que não são colunas diretas da tabela User)
    foto_barbeiro = forms.ImageField(required=False, label="Foto de Perfil")
    
    senha_atual = forms.CharField(
        required=False, widget=forms.PasswordInput, label="Senha Atual"
    )
    nova_senha = forms.CharField(
        required=False, widget=forms.PasswordInput, label="Nova Senha"
    )

    class Meta:
        # CONFIGURAÇÃO: Conecta este form à tabela User
        model = User
        fields = ['username', 'email', 'telefone']

    def __init__(self, *args, **kwargs):
        # INICIALIZAÇÃO: Roda quando o form é criado
        super().__init__(*args, **kwargs)
        
        # Preenche o campo 'foto_barbeiro' manualmente se o usuário já tiver um perfil
        if self.instance and hasattr(self.instance, 'barber'):
            self.fields['foto_barbeiro'].initial = self.instance.barber.foto_barbeiro

    # --- VALIDAÇÕES (CLEAN) ---

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        telefone_limpo = ''.join(filter(str.isdigit, str(telefone)))
        
        if len(telefone_limpo) != 11:
            raise ValidationError("O telefone deve ter exatamente 11 dígitos.")
        
        # Verifica duplicidade (excluindo o usuário atual da busca)
        if User.objects.filter(telefone=telefone_limpo).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este telefone já está em uso por outro usuário.")

        return telefone_limpo

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Verifica duplicidade
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este nome de usuário já está em uso.")
        return username

    # --- ADICIONADO: Validação de E-mail ---
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Verifica se outro usuário já tem esse email
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Este e-mail já está cadastrado.")
            
        return email

    def clean(self):
        # Validação cruzada de senhas (mantida igual)
        cleaned_data = super().clean()
        senha_atual = cleaned_data.get('senha_atual')
        nova_senha = cleaned_data.get('nova_senha')

        if senha_atual or nova_senha:
            if not senha_atual:
                self.add_error('senha_atual', "Digite a senha atual para confirmar.")
            if not nova_senha:
                self.add_error('nova_senha', "Digite a nova senha.")
            
            if senha_atual and nova_senha:
                if not self.instance.check_password(senha_atual):
                    self.add_error('senha_atual', "Senha atual incorreta.")
                if len(nova_senha) < 8:
                     self.add_error('nova_senha', "A nova senha deve ter no mínimo 8 caracteres.")

        return cleaned_data