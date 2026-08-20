from django.contrib import admin

from cardapio.models import Categoria, Cliente, Pedido, Produto


class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "preco", "disponivel")
    list_display_links = ("nome",)
    list_editable = ("disponivel",)
    search_fields = ("nome",)
    list_filter = ("categoria",)
    list_per_page = 50


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativa")
    list_display_links = ("nome",)
    list_editable = ("ativa",)
    search_fields = ("nome",)
    list_per_page = 10


class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "telefone", "email")
    list_display_links = ("nome",)
    search_fields = ("nome",)
    list_per_page = 50


class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "get_cliente_nome")
    search_fields = ("cliente__nome",)
    list_per_page = 50

    @admin.display(description="Cliente")
    def get_cliente_nome(self, obj):
        return obj.cliente.nome


admin.site.register(Produto, ProdutoAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Pedido, PedidoAdmin)
