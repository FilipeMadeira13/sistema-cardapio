from cardapio.models import Produto

CARRINHO_SESSION_KEY = "carrinho"


def get_carrinho(request):
    return request.session.setdefault(CARRINHO_SESSION_KEY, {})


def adicionar_item(request, produto_id, quantidade=1):
    carrinho = get_carrinho(request)
    produto_id = str(produto_id)
    carrinho[produto_id] = carrinho.get(produto_id, 0) + quantidade
    request.session.modified = True


def remover_item(request, produto_id):
    carrinho = get_carrinho(request)
    carrinho.pop(str(produto_id), None)
    request.session.modified = True


def limpar_carrinho(request):
    request.session[CARRINHO_SESSION_KEY] = {}
    request.session.modified = True


def itens_do_carrinho(request):
    """Converte o dict da sessão em uma lista com os objetos Produto reais."""
    carrinho = get_carrinho(request)
    produtos = Produto.objects.filter(id__in=carrinho.keys())
    itens = []
    total = 0
    for produto in produtos:
        quantidade = carrinho[str(produto.pk)]
        subtotal = produto.preco * quantidade
        total += subtotal
        itens.append(
            {
                "produto": produto,
                "quantidade": quantidade,
                "subtotal": subtotal,
            }
        )
    return itens, total
