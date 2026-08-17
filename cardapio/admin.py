from django.contrib import admin

from cardapio.models import Categoria, Produto


class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "preco")


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome",)


admin.site.register(Produto, ProdutoAdmin)
admin.site.register(Categoria, CategoriaAdmin)
