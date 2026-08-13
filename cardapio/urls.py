from django.urls import path

from cardapio.views import index, menu

urlpatterns = [
    path("", index, name="index"),
    path("menu/", menu, name="menu"),
]
