from django.core.exceptions import ValidationError
from django.db import transaction

from cardapio.models import Cliente, ItemPedido, Pedido, Produto


@transaction.atomic
def criar_pedido(cliente_dados, itens_carrinho, cliente=None):
    """
    cliente_dados: dict com nome, telefone, email
    itens_carrinho: lista de dicts, ex: [{"produto": produto_obj, "quantidade": 2}, ...]
    """
    if not itens_carrinho:
        raise ValidationError("Não é possível criar um pedido sem itens.")

    itens_por_produto = {}
    for item in itens_carrinho:
        produto = item.get("produto")
        quantidade = item.get("quantidade")
        if not isinstance(produto, Produto) or not produto.disponivel:
            raise ValidationError("Um dos produtos não está disponível.")
        if not isinstance(quantidade, int) or quantidade < 1:
            raise ValidationError("A quantidade dos itens deve ser maior que zero.")
        itens_por_produto[produto.pk] = (
            itens_por_produto.get(produto.pk, 0) + quantidade
        )

    if cliente is None:
        cliente, _ = Cliente.objects.get_or_create(
            telefone=cliente_dados["telefone"],
            defaults={
                "nome": cliente_dados["nome"],
                "email": cliente_dados.get("email", ""),
            },
        )

    pedido = Pedido.objects.create(cliente=cliente)

    for produto_id, quantidade in itens_por_produto.items():
        produto = Produto.objects.get(pk=produto_id)
        ItemPedido.objects.create(
            pedido=pedido,
            produto=produto,
            quantidade=quantidade,
            preco_unitario=produto.preco,
        )

    pedido.full_clean()
    return pedido
