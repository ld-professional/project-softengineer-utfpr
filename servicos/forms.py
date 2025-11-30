from django import forms
from .models import Servicos # Ajuste o .models conforme necessário

class ServicoForm(forms.ModelForm):
    class Meta:
        model = Servicos
        # Liste todos os campos que você quer validar e salvar
        fields = ['nome_servico', 'preco_servico', 'slot_duracao_servico']
        
    # Se precisar de um campo de ID para edição, você pode adicioná-lo
    # como um campo oculto no template ou tratar via ModelForm