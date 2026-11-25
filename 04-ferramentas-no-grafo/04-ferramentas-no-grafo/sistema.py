"""O sistema de pedidos da Loja Exemplo.

Ele faz o que mandarem: não confere status nem cliente. Cada cancelamento ou troca fica
anotado em `efeitos`, que é o que os testes olham para saber se algo mudou de verdade.

Só usa a biblioteca padrão.
"""
from regras import ler_pedidos


class PedidoInexistente(Exception):
    """O sistema não tem pedido com esse número."""


class SistemaPedidos:
    def __init__(self):
        self.pedidos = ler_pedidos()
        self.efeitos = []

    def buscar(self, id_pedido):
        """Lê o pedido. Retorna uma cópia, ou None se ele não existe. Não muda nada."""
        pedido = self.pedidos.get(id_pedido)
        return dict(pedido) if pedido else None

    def cancelar(self, id_pedido):
        if id_pedido not in self.pedidos:
            raise PedidoInexistente(f'pedido {id_pedido}')
        self.pedidos[id_pedido]['status'] = 'cancelado'
        self.efeitos.append(('cancelar', id_pedido))

    def abrir_troca(self, id_pedido, motivo):
        if id_pedido not in self.pedidos:
            raise PedidoInexistente(f'pedido {id_pedido}')
        self.efeitos.append(('troca', id_pedido, motivo))
