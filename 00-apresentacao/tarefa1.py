"""Tarefa 1 do diagnóstico: o reembolso que não pode sair duas vezes."""
import csv
from pathlib import Path

PEDIDOS = Path(__file__).resolve().parent.parent / 'dados' / 'loja' / 'pedidos.csv'


def carregar():
    """Retorna {id_pedido (int): {'cliente': ..., 'valor': float, 'status': ...}}."""
    with open(PEDIDOS, encoding='utf-8', newline='') as f:
        return {int(p['id_pedido']): {'cliente': p['cliente'], 'valor': float(p['valor']), 'status': p['status']}
                for p in csv.DictReader(f)}


def reembolsar(pedidos, registro, id_pedido, valor, chave):
    """Grava o reembolso em `registro` uma vez só por chave e retorna 'feito' ou 'repetido'.

    Escreva aqui a sua função. As regras estão na tarefa 1 do diagnóstico.
    """
    raise NotImplementedError('escreva a função reembolsar')


def reais(valor):
    return 'R$ ' + f'{valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')


if __name__ == '__main__':
    pedidos = carregar()
    print('pedidos no arquivo:', len(pedidos))
    registro = []
    # A segunda chamada repete a primeira, como depois de uma queda no meio do atendimento.
    for id_pedido, valor, chave in ((52, 79.90, 'r-52-1'), (52, 79.90, 'r-52-1'), (7, 850.00, 'r-7-1')):
        print(f'{chave}: {reembolsar(pedidos, registro, id_pedido, valor, chave)}')
    print(f'reembolsos gravados: {len(registro)}; total: {reais(sum(r["valor"] for r in registro))}')
