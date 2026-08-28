# Backlog — Sistema de Cardápio de Restaurante (Django)

Projeto para praticar Models, ORM e Django Admin. As regras abaixo servem
como guia; ajuste conforme for evoluindo o projeto.

---

## 1. Visão geral

Sistema onde um restaurante cadastra seu cardápio (categorias e produtos)
e recebe pedidos de clientes. A gestão do cardápio e dos pedidos acontece
principalmente pelo **Django Admin**.

---

## 2. Entidades principais

- **Categoria** (ex: Entradas, Pratos principais, Bebidas, Sobremesas)
- **Produto** (item do cardápio, pertence a uma Categoria)
- **Cliente**
- **Pedido**
- **ItemPedido** (produto + quantidade dentro de um pedido)

---

## 3. Regras de negócio


### Pedido
- [ ] O valor total do pedido é calculado automaticamente a partir da
      soma dos itens (quantidade × preço do produto no momento do
      pedido), nunca digitado manualmente.
- [ ] Data/hora do pedido é preenchida automaticamente na criação
      (`auto_now_add`).
- [ ] Pedido cancelado não pode voltar para outro status.

### ItemPedido
- [ ] Relaciona um Pedido a um Produto, com uma quantidade.
- [ ] Quantidade deve ser maior que zero.
- [ ] O preço do produto deve ser "congelado" no item do pedido (salvo
      no momento da compra), para que alterações futuras no preço do
      produto não mudem pedidos antigos.
- [ ] Não pode haver dois `ItemPedido` do mesmo produto duplicados no
      mesmo pedido — nesse caso, deve-se atualizar a quantidade do item
      já existente.

---

## 4. Django Admin — o que customizar

- [ ] `list_display` em Produto mostrando: nome, categoria, preço,
      disponibilidade.
- [ ] Filtros (`list_filter`) por categoria e disponibilidade.
- [ ] Busca (`search_fields`) por nome do produto e nome do cliente.
- [ ] Inline de `ItemPedido` dentro da tela de `Pedido` (para
      adicionar/ver itens sem sair da página do pedido).
- [ ] `list_display` em Pedido mostrando: cliente, status, data, total.
- [ ] Ação em massa (admin action) para marcar vários pedidos como
      "Entregue" de uma vez.

---

## 5. Possíveis evoluções (fora do escopo inicial)

- Autenticação de clientes (login).
- Formulário público para o cliente montar o próprio pedido (fora do admin).
- Cálculo de frete / taxa de entrega.
- Relatório de produtos mais vendidos (usando agregação do ORM).
- Sistema de cupons de desconto.

---

## 6. Anotações livres

> Use esta seção para anotar dúvidas, decisões tomadas e coisas para
> revisar depois.

-
