from django.shortcuts import render


def index(request):
    return render(request, "cardapio/index.html")


def menu(request):
    dados = {
        1: {
            "nome": "Frango Assado",
            "descricao": "O melhor frango assado da cidade.",
            "preco": 27.00,
        },
        2: {
            "nome": "Prato Feito",
            "descricao": "Delicioso prato com opções variádas.",
            "preco": 19.00,
        },
    }
    return render(request, "cardapio/menu.html", {"pratos": dados})
