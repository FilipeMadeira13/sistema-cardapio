from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from cardapio.forms import CadastroForms
from cardapio.models import Categoria, Cliente, Produto
from cardapio.services import criar_pedido

from . import carrinho as carrinho_service


def index(request):
    return render(request, "cardapio/index.html")


def menu(request):
    produtos_disponiveis = Produto.objects.filter(disponivel=True)
    categorias = (
        Categoria.objects.filter(
            ativa=True,
            produtos__disponivel=True,
        )
        .prefetch_related(Prefetch("produtos", queryset=produtos_disponiveis))
        .distinct()
    )

    return render(request, "cardapio/menu.html", {"categorias": categorias})


def adicionar_ao_carrinho(request, produto_id):
    if request.method != "POST":
        return redirect("menu")
    produto = get_object_or_404(Produto, id=produto_id, disponivel=True)
    carrinho_service.adicionar_item(request, produto_id)
    messages.success(request, f'"{produto.nome}" adicionado ao carrinho.')
    return redirect("menu")


def remover_do_carrinho(request, produto_id):
    if request.method != "POST":
        return redirect("ver_carrinho")
    carrinho_service.remover_item(request, produto_id)
    return redirect("ver_carrinho")


def ver_carrinho(request):
    itens, total = carrinho_service.itens_do_carrinho(request)
    return render(request, "cardapio/carrinho.html", {"itens": itens, "total": total})


def cadastro(request):
    if request.method == "POST":
        form = CadastroForms(request.POST)
        if form.is_valid():
            user = form.save()
            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )
            return redirect("checkout")
    else:
        form = CadastroForms()
    return render(request, "cardapio/cadastro.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("index")


@login_required
def checkout(request):
    itens, total = carrinho_service.itens_do_carrinho(request)

    if not itens:
        return render(
            request,
            "cardapio/carrinho.html",
            {
                "itens": itens,
                "total": total,
                "erro": "Seu carrinho está vazio.",
            },
        )

    if request.method == "POST":
        cliente = get_object_or_404(Cliente, usuario=request.user)
        itens_carrinho = [
            {"produto": item["produto"], "quantidade": item["quantidade"]}
            for item in itens
        ]
        try:
            pedido = criar_pedido(
                cliente_dados={
                    "nome": cliente.nome,
                    "telefone": cliente.telefone,
                    "email": cliente.email,
                },
                itens_carrinho=itens_carrinho,
                cliente=cliente,
            )
        except ValidationError as e:
            return render(
                request,
                "cardapio/carrinho.html",
                {
                    "itens": itens,
                    "total": total,
                    "erro": str(e),
                },
            )

        carrinho_service.limpar_carrinho(request)
        return redirect("pedido_confirmado", pk=pedido.pk)

    return render(request, "cardapio/checkout.html", {"itens": itens, "total": total})


@login_required
def pedido_confirmado(request, pk):
    from cardapio.models import Pedido

    pedido = get_object_or_404(Pedido, pk=pk, cliente__usuario=request.user)
    return render(request, "cardapio/pedido_confirmado.html", {"pedido": pedido})
