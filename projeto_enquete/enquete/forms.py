from django import forms
from .models import Enquete, Pergunta, Opcao, Area, Resposta, MultiplaEscolhaResposta
from django.forms import inlineformset_factory

class EstiloFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class AreaForm(EstiloFormMixin, forms.ModelForm):
    class Meta:
        model = Area
        fields = ['nome', 'descricao']

class EnqueteForm(EstiloFormMixin, forms.ModelForm):
    class Meta:
        model = Enquete
        fields = ['titulo', 'descricao', 'ativa', 'area', 'tecnologias']
        widgets = {
            'tecnologias': forms.CheckboxSelectMultiple(),
        }

class PerguntaForm(EstiloFormMixin, forms.ModelForm):
    class Meta:
        model = Pergunta
        fields = ['texto', 'tipo', 'enquete', 'tecnologia', 'ativa']
        widgets = {
            'enquete': forms.HiddenInput(),
        }

class OpcaoForm(EstiloFormMixin, forms.ModelForm):
    class Meta:
        model = Opcao
        fields = ['texto', 'ativa', 'ordem', 'peso']
        # 'pergunta' não precisa ser HiddenInput aqui se for setado na view
        # widgets = {
        #     'pergunta': forms.HiddenInput(),
        # }

OpcaoFormSet = inlineformset_factory(Pergunta, Opcao, form=OpcaoForm, extra=3, can_delete=True)

class RespostaForm(forms.Form):
    # RadioSelect para única escolha
    opcao = forms.ModelChoiceField(queryset=Opcao.objects.none(), widget=forms.RadioSelect, label="Opção")

    def __init__(self, pergunta, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra as opções pela pergunta específica
        self.fields['opcao'].queryset = pergunta.opcao_set.filter(ativa=True)

class MultiplaEscolhaRespostaForm(forms.Form):
    # CheckboxSelectMultiple para múltipla escolha
    opcoes = forms.ModelMultipleChoiceField(queryset=Opcao.objects.none(), widget=forms.CheckboxSelectMultiple, label="Opções")

    def __init__(self, pergunta, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra as opções pela pergunta específica
        self.fields['opcoes'].queryset = pergunta.opcao_set.filter(ativa=True)
