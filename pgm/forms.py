from django import forms


class UploadFileForm(forms.Form):
    arquivo = forms.FileField()

class UploadProcessosForm(forms.Form):
    arquivo = forms.FileField()

class FilterOneForm(forms.Form):
    vencimento_de = forms.DateField(label='Vencimento de', widget=forms.TextInput(
        attrs={
            'class':'js-datepicker form-control',
            'autocomplete':'off'
        }
    ))
    vencimento_ate = forms.DateField(label='Vencimento até', widget=forms.TextInput(
        attrs={
            'class':'js-datepicker form-control',
            'autocomplete': 'off'
        }
    ))
    codigo_receita = forms.IntegerField(label='Código Receita',initial='1715', widget=forms.TextInput(
        attrs={
            'class': 'form-control'
        }
    ))
    valor_de = forms.CharField(label='Valor Inicial', widget=forms.TextInput(
        attrs={
            'class':'moneymask form-control',
            'autocomplete': 'off'
        }
    ))
    valor_ate = forms.CharField(label='Valor Final', widget=forms.TextInput(
        attrs={
            'class':'moneymask form-control',
            'autocomplete': 'off'
        }
    ))
    ajuizado = forms.ChoiceField(label='Ajuizado?', choices=(('nao', 'Não'), ('sim', 'Sim')), widget=forms.Select(
        attrs={
            'class': 'form-control'
        }
    ))


class BuscarForm(forms.Form):
    cpf_cnpj = forms.CharField(label='CPF/CNPJ nº', widget=forms.TextInput(
        attrs={
            'autocomplete':'off'
        }
    ))
