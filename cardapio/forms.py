from typing import Any

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from cardapio.models import Cliente


class CadastroForms(UserCreationForm):
    nome = forms.CharField(max_length=150)
    telefone = forms.CharField(max_length=50)
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]

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
