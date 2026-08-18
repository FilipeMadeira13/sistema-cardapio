from django.shortcuts import render

from cardapio.models import Categoria


def index(request):
    return render(request, "cardapio/index.html")


def menu(request):
    categorias = Categoria.objects.filter(ativa=True).prefetch_related("produtos").all()

    return render(request, "cardapio/menu.html", {"categorias": categorias})
