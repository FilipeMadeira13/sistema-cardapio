from django.shortcuts import render


def index(request):
    return render(request, "cardapio/index.html")


def menu(request):
    return render(request, "cardapio/menu.html")
