from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Categoria, Cliente, ItemPedido, Pedido, Produto
from .services import criar_pedido


class PedidoTest(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nome="Pratos")
        self.produto = Produto.objects.create(
            nome="Feijoada",
            descricao="Feijoada completa",
            preco=35.00,
            categoria=self.categoria,
        )

    # --- Regra: pelo menos 1 item ---

    def test_nao_pode_criar_pedido_sem_itens(self):
        with self.assertRaises(ValidationError):
            criar_pedido(
                cliente_dados={"nome": "Teste", "telefone": "11999990001"},
                itens_carrinho=[],
            )

    def test_cria_pedido_com_itens_com_sucesso(self):
        pedido = criar_pedido(
            cliente_dados={"nome": "Teste", "telefone": "11999990002"},
            itens_carrinho=[{"produto": self.produto, "quantidade": 2}],
        )
        self.assertEqual(pedido.itens.count(), 1)

    def test_nao_pode_remover_ultimo_item(self):
        pedido = criar_pedido(
            cliente_dados={"nome": "Teste", "telefone": "11999990003"},
            itens_carrinho=[{"produto": self.produto, "quantidade": 1}],
        )
        item = pedido.itens.first()
        with self.assertRaises(ValidationError):
            item.delete()

    def test_pode_remover_item_se_sobrar_outro(self):
        pedido = criar_pedido(
            cliente_dados={"nome": "Teste", "telefone": "11999990004"},
            itens_carrinho=[
                {"produto": self.produto, "quantidade": 1},
                {"produto": self.produto, "quantidade": 2},
            ],
        )
        item = pedido.itens.first()
        item.delete()  # não deve levantar erro, pois sobra 1
        self.assertEqual(pedido.itens.count(), 1)

    # --- Regra: transição de status ---

    def test_fluxo_completo_de_status_valido(self):
        pedido = criar_pedido(
            cliente_dados={"nome": "Teste", "telefone": "11999990005"},
            itens_carrinho=[{"produto": self.produto, "quantidade": 1}],
        )
        pedido.status = Pedido.Status.EM_PREPARO
        pedido.full_clean()
        pedido.save()

        pedido.status = Pedido.Status.PRONTO
        pedido.full_clean()
        pedido.save()

        pedido.status = Pedido.Status.ENTREGUE
        pedido.full_clean()
        pedido.save()

        self.assertEqual(pedido.status, Pedido.Status.ENTREGUE)

    def test_nao_pode_pular_etapa_de_status(self):
        pedido = criar_pedido(
            cliente_dados={"nome": "Teste", "telefone": "11999990006"},
            itens_carrinho=[{"produto": self.produto, "quantidade": 1}],
        )
        pedido.status = Pedido.Status.PRONTO  # pulando EM_PREPARO
        with self.assertRaises(ValidationError):
            pedido.full_clean()

    def test_nao_pode_mudar_status_apos_entregue(self):
        pedido = criar_pedido(
            cliente_dados={"nome": "Teste", "telefone": "11999990007"},
            itens_carrinho=[{"produto": self.produto, "quantidade": 1}],
        )
        pedido.status = Pedido.Status.EM_PREPARO
        pedido.save()
        pedido.status = Pedido.Status.PRONTO
        pedido.save()
        pedido.status = Pedido.Status.ENTREGUE
        pedido.save()

        pedido.status = Pedido.Status.CANCELADO
        with self.assertRaises(ValidationError):
            pedido.full_clean()
