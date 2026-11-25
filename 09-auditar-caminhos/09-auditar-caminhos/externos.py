"""A operadora do cartão, de fora da loja. A mesma da aula 08, agora com as cobranças.

Ela é de mentira: nenhum dinheiro sai de verdade. A lista `pagamentos` é o dinheiro saindo.
Como na aula 08, ela aceita uma chave: a mesma chave na segunda chamada retorna o estorno que já
foi feito, sem estornar de novo. E sabe cair de propósito: `cair('antes')` cai sem estornar,
`cair('depois')` estorna e cai antes de responder. Do lado da loja, as duas quedas chegam iguais:
a exceção ForaDoAr.

O que muda: a operadora só estorna o que ela cobrou. Pedido que ainda espera pagamento não tem
cobrança, e o estorno dele é recusado com a exceção Recusado. Isso não é queda: tentar de novo
dá a mesma recusa.
"""
import csv
from pathlib import Path

ARQUIVO = Path(__file__).resolve().parent.parent / 'dados' / 'loja' / 'pedidos.csv'
COBRADOS = ('em_separacao', 'enviado', 'entregue')  # status de pedido que já foi pago


class ForaDoAr(Exception):
    """A operadora não respondeu. Não dá para saber, por aqui, se o estorno aconteceu."""


class Recusado(Exception):
    """A operadora respondeu que não faz esse estorno. Tentar de novo não muda a resposta."""


def pedidos_cobrados():
    with open(ARQUIVO, encoding='utf-8') as f:
        return {int(p['id_pedido']) for p in csv.DictReader(f) if p['status'] in COBRADOS}


class Operadora:
    """A operadora do cartão. `estornar` devolve o dinheiro de um pedido que ela cobrou."""

    def __init__(self):
        self.cobrados = pedidos_cobrados()
        self.pagamentos = []  # um item por estorno feito: é o dinheiro saindo
        self.chamadas = 0
        self._quedas = []
        self._feitos = {}  # chave -> o estorno feito com ela

    def cair(self, quando):
        """A próxima chamada cai: 'antes' de estornar ou 'depois' de estornar."""
        assert quando in ('antes', 'depois'), quando
        self._quedas.append(quando)

    def estornar(self, id_pedido, valor, chave=None):
        self.chamadas += 1
        queda = self._quedas.pop(0) if self._quedas else None
        if queda == 'antes':
            raise ForaDoAr('a operadora não respondeu')
        dados = {'id_pedido': id_pedido, 'valor': valor}
        if chave is not None and chave in self._feitos:
            feito = self._feitos[chave]
            if {k: feito[k] for k in dados} != dados:
                raise ValueError(f'a chave {chave} já foi usada com outros dados')
        else:
            if id_pedido not in self.cobrados:
                raise Recusado(f'o pedido {id_pedido} não tem cobrança para estornar')
            feito = {'id_pagamento': f'E{len(self.pagamentos) + 1:03d}', **dados}
            self.pagamentos.append(feito)
            if chave is not None:
                self._feitos[chave] = feito
        if queda == 'depois':
            raise ForaDoAr('a operadora não respondeu')
        return dict(feito)
