from django import forms
from django.core.exceptions import ValidationError
# Importamos a lista oficial do seu models para garantir que seja sempre igual
from barbeiro.models import dias_da_semana 

class FormularioAgenda(forms.Form):
    
    # TypedMultipleChoiceField valida se o valor está na lista E converte para Inteiro
    dias_semana = forms.TypedMultipleChoiceField(
        choices=dias_da_semana, # Usa [(0, 'Segunda'), (1, 'Terça')...] # as strings "segunda e etc n sao usadas aqui" ja q ja eh numero
        coerce=int,  # igual do pandas           # <--- O PULO DO GATO: Converte "0" (str) virar 0 (int)
        required=True,
        error_messages={
            'required': 'Selecione pelo menos um dia da semana.',
            'invalid_choice': 'Dia inválido.',
        }
    )

    horario_inicio = forms.TimeField(
        required=True,
        widget=forms.TimeInput(format='%H:%M'),
        error_messages={'required': 'Informe a hora de início.', 'invalid': 'Hora inválida.'}
    )

    horario_fim = forms.TimeField(
        required=True,
        widget=forms.TimeInput(format='%H:%M'),
        error_messages={'required': 'Informe a hora de término.', 'invalid': 'Hora inválida.'}
    )


    #def clean_dias_da_semana(self): desnecessario pq ja uso coerce e choice, logo o django ja faz isso...




    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('horario_inicio')
        fim = cleaned_data.get('horario_fim')

        if inicio and fim and inicio >= fim:
            raise ValidationError("A hora de término deve ser depois da hora de início.")
        
        return cleaned_data