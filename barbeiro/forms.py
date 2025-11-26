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