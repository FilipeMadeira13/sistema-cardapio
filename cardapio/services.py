from django.core.exceptions import ValidationError
from django.db import transaction

from cardapio.models import Cliente, ItemPedido, Pedido


@transaction.atomic
def criar_pedido(cliente_dados, itens_carrinho):
    """
    cliente_dados: dict com nome, telefone, email
    itens_carrinho: lista de dicts, ex: [{"produto": produto_obj, "quantidade": 2}, ...]
    """
    if not itens_carrinho:
        raise ValidationError("Não é possível criar um pedido sem itens.")

    cliente, _ = Cliente.objects.get_or_create(
        telefone=cliente_dados["telefone"],
        defaults={
            "nome": cliente_dados["nome"],
            "email": cliente_dados.get("email", ""),
        },
    )

    pedido = Pedido.objects.create(cliente=cliente)

    for item in itens_carrinho:
        ItemPedido.objects.create(
            pedido=pedido,
            produto=item["produto"],
            quantidade=item["quantidade"],
            preco_unitario=item["produto"].preco,
        )

    pedido.full_clean()
    return pedido
