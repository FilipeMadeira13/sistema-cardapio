from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True, null=False, blank=False)
    ativa = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=100, null=False, blank=False)
    descricao = models.TextField(null=False, blank=False)
    preco = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=False
    )
    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, related_name="produtos"
    )
    imagem = models.ImageField(upload_to="imagens/%Y/%m/%d/", blank=True)
    disponivel = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.nome
