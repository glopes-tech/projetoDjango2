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
        # widgets = {
        #     'pergunta': forms.HiddenInput(),
        # }

OpcaoFormSet = inlineformset_factory(Pergunta, Opcao, form=OpcaoForm, extra=3, can_delete=True)

class RespostaForm(forms.Form): 
    def __init__(self, *args, **kwargs):
        # O argumento 'pergunta' é extraído dos kwargs.
        # Isso garante que 'pergunta' não seja passado para o __init__ do formulário base do Django.
        self.pergunta = kwargs.pop('pergunta') 
        super().__init__(*args, **kwargs)

        # O nome do campo é dinâmico e depende do ID da pergunta para evitar conflitos
        field_name = f'pergunta_{self.pergunta.id}'

        if self.pergunta.tipo == Pergunta.UNICA_ESCOLHA:
            opcoes_disponiveis = self.pergunta.opcao_set.filter(ativa=True)
            self.fields[field_name] = forms.ModelChoiceField(
                queryset=opcoes_disponiveis,
                widget=forms.RadioSelect,
                empty_label=None, # Garante que uma opção deve ser selecionada
                required=True,
                label=self.pergunta.texto # O label do campo é o texto da pergunta
            )
        elif self.pergunta.tipo == Pergunta.MULTIPLA_ESCOLHA:
            opcoes_disponiveis = self.pergunta.opcao_set.filter(ativa=True)
            self.fields[field_name] = forms.ModelMultipleChoiceField(
                queryset=opcoes_disponiveis,
                widget=forms.CheckboxSelectMultiple,
                required=True, # Garante que pelo menos uma opção deve ser selecionada
                label=self.pergunta.texto # O label do campo é o texto da pergunta
            )

#class MultiplaEscolhaRespostaForm(forms.Form):
#    opcoes = forms.ModelMultipleChoiceField(queryset=Opcao.objects.none(), widget=forms.CheckboxSelectMultiple, label="Opções")

#    def __init__(self, pergunta, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        self.fields['opcoes'].queryset = pergunta.opcao_set.filter(ativa=True)
