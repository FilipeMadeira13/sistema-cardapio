from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
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
        validators=[MinValueValidator(0.01)],
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
                condition=models.Q(preco__gt=0),
                name="preco_positivo",
            )
        ]

    def __str__(self) -> str:
        return self.nome


class Cliente(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cliente",
        null=True,
        blank=True,
    )
    nome = models.CharField(max_length=150, blank=False)
    telefone = models.CharField(max_length=50, blank=False, unique=True)
    email = models.EmailField(max_length=100, blank=True)

    def __str__(self) -> str:
        return self.nome


class Pedido(models.Model):
    class Status(models.TextChoices):
        RECEBIDO = "RECEBIDO", "Recebido"
        EM_PREPARO = "EM_PREPARO", "Em preparo"
        PRONTO = "PRONTO", "Pronto"
        ENTREGUE = "ENTREGUE", "Entregue"
        CANCELADO = "CANCELADO", "Cancelado"

    TRANSACOES_VALIDAS = {
        Status.RECEBIDO: [Status.EM_PREPARO, Status.CANCELADO],
        Status.EM_PREPARO: [Status.PRONTO, Status.CANCELADO],
        Status.PRONTO: [Status.ENTREGUE, Status.CANCELADO],
        Status.ENTREGUE: [],
        Status.CANCELADO: [],
    }

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="pedidos",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RECEBIDO,
    )

    def clean(self):
        if self.pk:
            status_atual = self.Status(Pedido.objects.get(pk=self.pk).status)
            if status_atual != self.status:
                if self.status not in self.TRANSACOES_VALIDAS[status_atual]:
                    raise ValidationError(
                        f"Não é possível mudar de '{status_atual}' para '{self.status}'."
                    )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Pedido #{self.pk} — {self.cliente.nome}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="itens",
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name="itens_pedido",
    )
    quantidade = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantidade__gte=1),
                name="quantidade_positiva",
            )
        ]

    def __str__(self) -> str:
        return f"{self.quantidade}x {self.produto.nome}"

    def delete(self, *args, **kwargs):
        if self.pedido.itens.count() <= 1:
            raise ValidationError(
                "Não é possível remover o último item — o pedido ficaria vazio."
            )
        super().delete(*args, **kwargs)
