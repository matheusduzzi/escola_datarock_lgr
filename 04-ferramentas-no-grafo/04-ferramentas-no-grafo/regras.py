"""Regras do cancelamento da Loja Exemplo.

Só usa a biblioteca padrão. Rode sozinho para ver o que a regra diz para os pedidos da Cliente 0036:

    python3 regras.py
"""
import csv
from pathlib import Path

PASTA = Path(__file__).resolve().parent
PEDIDOS_CSV = PASTA.parent / 'dados' / 'loja' / 'pedidos.csv'

PODE_CANCELAR = ('aguardando_pagamento', 'em_separacao')
STATUS = {'aguardando_pagamento': 'aguardando pagamento', 'em_separacao': 'em separação',
          'enviado': 'enviado', 'entregue': 'entregue', 'cancelado': 'cancelado'}


def motivo_para_nao_cancelar(pedido, cliente):
    """Retorna None se o pedido pode ser cancelado, ou o motivo da recusa.

    Pedido que não existe e pedido de outra pessoa recebem o mesmo motivo: o atendimento
    não conta para um cliente que o pedido de outra pessoa existe.
    """
    if pedido is None or pedido['cliente'] != cliente:
        return 'esse pedido não está no seu cadastro'
    if pedido['status'] not in PODE_CANCELAR:
        return f"o pedido {pedido['id_pedido']} já está {STATUS[pedido['status']]}"
    return None


def ler_pedidos(caminho=PEDIDOS_CSV):
    with open(caminho, encoding='utf-8', newline='') as f:
        return {int(p['id_pedido']): p for p in csv.DictReader(f)}


if __name__ == '__main__':
    pedidos = ler_pedidos()
    for numero in (40, 78, 109, 27, 999):
        motivo = motivo_para_nao_cancelar(pedidos.get(numero), 'Cliente 0036')
        print(f'pedido {numero:<4} {motivo or "pode cancelar"}')
