from typing import cast

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction

from cardapio.models import Cliente, ItemPedido, Produto


class CadastroForms(UserCreationForm):
    nome = forms.CharField(max_length=150)
    telefone = forms.CharField(max_length=50)
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]

    def clean_telefone(self):
        telefone = self.cleaned_data["telefone"]
        if Cliente.objects.filter(telefone=telefone).exists():
            raise forms.ValidationError("Este telefone já está cadastrado.")
        return telefone

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()
            Cliente.objects.create(
                usuario=user,
                nome=self.cleaned_data["nome"],
                telefone=self.cleaned_data["telefone"],
                email=self.cleaned_data.get("email", ""),
            )

        return user


class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ["produto", "quantidade"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        produto_field = cast(forms.ModelChoiceField, self.fields["produto"])
        produto_field.queryset = Produto.objects.filter(disponivel=True)
