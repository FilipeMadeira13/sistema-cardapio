from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

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
        self.outro_produto = Produto.objects.create(
            nome="Suco",
            descricao="Suco natural",
            preco=8.00,
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
                {"produto": self.outro_produto, "quantidade": 2},
            ],
        )
        item = pedido.itens.first()
        item.delete()  # não deve levantar erro, pois sobra 1
        self.assertEqual(pedido.itens.count(), 1)

    def test_consolida_produtos_duplicados(self):
        pedido = criar_pedido(
            cliente_dados={"nome": "Teste", "telefone": "11999990008"},
            itens_carrinho=[
                {"produto": self.produto, "quantidade": 1},
                {"produto": self.produto, "quantidade": 2},
            ],
        )
        item = pedido.itens.get()
        self.assertEqual(item.quantidade, 3)

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


class FluxoCarrinhoCheckoutTest(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nome="Pratos")
        self.produto = Produto.objects.create(
            nome="Feijoada",
            descricao="Feijoada completa",
            preco=35.00,
            categoria=self.categoria,
        )

    def test_cadastro_cria_user_e_cliente_vinculados(self):
        response = self.client.post(
            reverse("cadastro"),
            {
                "username": "joaosilva",
                "password1": "SenhaForte123!",
                "password2": "SenhaForte123!",
                "nome": "João Silva",
                "telefone": "11988887777",
                "email": "joao@example.com",
            },
        )
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertTrue(hasattr(user, "cliente"))
        self.assertEqual(user.cliente.nome, "João Silva")
        # após cadastro, o usuário deve estar logado automaticamente
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_adicionar_produto_ao_carrinho_guarda_na_sessao(self):
        self.client.post(reverse("adicionar_ao_carrinho", args=[self.produto.pk]))
        session = self.client.session
        self.assertIn(str(self.produto.id), session.get("carrinho", {}))
        self.assertEqual(session["carrinho"][str(self.produto.pk)], 1)

    def test_checkout_exige_login(self):
        response = self.client.get(reverse("checkout"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_checkout_com_carrinho_vazio_mostra_erro(self):
        User.objects.create_user(username="teste", password="SenhaForte123!")
        Cliente.objects.create(
            usuario=User.objects.get(username="teste"),
            nome="Teste",
            telefone="11999998888",
        )
        self.client.login(username="teste", password="SenhaForte123!")

        response = self.client.get(reverse("checkout"))
        self.assertContains(response, "vazio")

    def test_fluxo_completo_de_compra(self):
        user = User.objects.create_user(username="maria", password="SenhaForte123!")
        Cliente.objects.create(usuario=user, nome="Maria", telefone="11977776666")
        self.client.login(username="maria", password="SenhaForte123!")

        # adiciona item ao carrinho
        self.client.post(reverse("adicionar_ao_carrinho", args=[self.produto.pk]))

        # confirma o pedido
        response = self.client.post(reverse("checkout"))
        self.assertEqual(response.status_code, 302)  # redireciona para confirmação

        pedido = Pedido.objects.get(cliente__usuario=user)
        self.assertEqual(pedido.itens.count(), 1)
        self.assertEqual(pedido.status, Pedido.Status.RECEBIDO)

        # carrinho deve ter sido limpo após o checkout
        session = self.client.session
        self.assertEqual(session.get("carrinho", {}), {})

    def test_checkout_exige_login(self):
        response = self.client.get(reverse("checkout"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("login")))
