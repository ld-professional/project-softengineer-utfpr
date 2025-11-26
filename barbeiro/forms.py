from django import forms
from .models import Horarios_de_trabalho, dias_da_semana

class HorariosTrabalhoMultiDiaForm(forms.ModelForm):

    dias = forms.MultipleChoiceField(
        choices=dias_da_semana,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Dias da semana"
    )

    class Meta:
        model = Horarios_de_trabalho
        fields = ['fk_barbeiro', 'hora_inicio', 'hora_fim']

