from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("cardapio/", views.menu, name="menu"),
    path("carrinho/", views.ver_carrinho, name="ver_carrinho"),
    path(
        "carrinho/adicionar/<int:produto_id>/",
        views.adicionar_ao_carrinho,
        name="adicionar_ao_carrinho",
    ),
    path(
        "carrinho/remover/<int:produto_id>/",
        views.remover_do_carrinho,
        name="remover_do_carrinho",
    ),
    path("checkout/", views.checkout, name="checkout"),
    path(
        "pedido/<int:pk>/confirmado/", views.pedido_confirmado, name="pedido_confirmado"
    ),
    path("cadastro/", views.cadastro, name="cadastro"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="cardapio/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="index"), name="logout"),
]
