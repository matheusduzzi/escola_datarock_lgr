"""O sistema de pedidos da Loja Exemplo, com falha que você escolhe.

    SistemaPedidos()            responde sempre
    SistemaPedidos(falhas=2)    as 2 primeiras consultas falham, depois responde
    SistemaPedidos(falhas=None) fora do ar: toda consulta falha

Só usa a biblioteca padrão.
"""
import csv

from regras import PEDIDOS_CSV


class SistemaFora(Exception):
    """A consulta não chegou ao sistema de pedidos."""


class SistemaPedidos:
    def __init__(self, falhas=0, caminho=PEDIDOS_CSV):
        with open(caminho, encoding='utf-8', newline='') as f:
            self.pedidos = {int(p['id_pedido']): p for p in csv.DictReader(f)}
        self.falhas = falhas
        self.chamadas = 0

    def buscar(self, id_pedido):
        """Retorna o pedido, ou None se ele não existe. Levanta SistemaFora quando falha."""
        self.chamadas += 1
        if self.falhas is None or self.chamadas <= self.falhas:
            raise SistemaFora(f'consulta {self.chamadas} sem resposta')
        return self.pedidos.get(id_pedido)
