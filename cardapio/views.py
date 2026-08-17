from django.shortcuts import render

from cardapio.models import Produto


def index(request):
    return render(request, "cardapio/index.html")


def menu(request):
    produtos = Produto.objects.all()

    return render(request, "cardapio/menu.html", {"produtos": produtos})
