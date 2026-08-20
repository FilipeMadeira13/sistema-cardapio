from django.core.validators import MinValueValidator
from django.db import models


class Categoria(models.Model):
    nome = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
    )
    ativa = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=100, null=False, blank=False)
    descricao = models.TextField(null=False, blank=False)
    preco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=False,
        validators=[MinValueValidator(0)],
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name="produtos",
    )
    imagem = models.ImageField(upload_to="imagens/%Y/%m/%d/", blank=True)
    disponivel = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(preco__gte=0),
                name="preco_nao_negativo",
            )
        ]

    def __str__(self) -> str:
        return self.nome


class Cliente(models.Model):
    nome = models.CharField(max_length=150, blank=False)
    telefone = models.CharField(max_length=50, blank=False, unique=True)
    email = models.EmailField(max_length=100, blank=True)

    def __str__(self) -> str:
        return self.nome


class Pedido(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="pedidos",
    )
