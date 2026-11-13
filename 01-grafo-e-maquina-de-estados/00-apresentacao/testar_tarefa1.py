"""Testes da tarefa 1. Rode com: python3 testar_tarefa1.py"""
import copy
import sys

from tarefa1 import carregar, reembolsar

PEDIDOS = carregar()


def espera_erro(funcao, *args):
    try:
        funcao(*args)
    except ValueError:
        return
    raise AssertionError(f'esperava ValueError com {args[2:]}')


def teste_primeira_chamada_grava():
    pedidos, registro = copy.deepcopy(PEDIDOS), []
    assert reembolsar(pedidos, registro, 52, 79.90, 'a') == 'feito'
    assert registro == [{'chave': 'a', 'id_pedido': 52, 'valor': 79.90}], registro


def teste_repeticao_nao_duplica():
    pedidos, registro = copy.deepcopy(PEDIDOS), []
    reembolsar(pedidos, registro, 52, 79.90, 'a')
    assert reembolsar(pedidos, registro, 52, 79.90, 'a') == 'repetido'
    assert len(registro) == 1, registro


def teste_mesma_chave_para_outro_reembolso():
    pedidos, registro = copy.deepcopy(PEDIDOS), []
    reembolsar(pedidos, registro, 52, 79.90, 'a')
    espera_erro(reembolsar, pedidos, registro, 7, 850.00, 'a')
    assert len(registro) == 1, registro


def teste_pedido_que_nao_existe():
    pedidos, registro = copy.deepcopy(PEDIDOS), []
    espera_erro(reembolsar, pedidos, registro, 999, 10.00, 'b')
    assert registro == [], registro


def teste_valor_fora_do_pedido():
    pedidos, registro = copy.deepcopy(PEDIDOS), []
    for valor in (0, -5.00, 79.91):
        espera_erro(reembolsar, pedidos, registro, 52, valor, f'c{valor}')
    assert registro == [], registro


def teste_pedidos_intactos():
    pedidos, registro = copy.deepcopy(PEDIDOS), [{'chave': 'antigo', 'id_pedido': 7, 'valor': 850.00}]
    antigo = registro[0]
    reembolsar(pedidos, registro, 52, 79.90, 'd')
    reembolsar(pedidos, registro, 52, 79.90, 'd')
    assert pedidos == PEDIDOS, 'a função alterou os pedidos'
    assert registro[0] is antigo and len(registro) == 2, registro


TESTES = [teste_primeira_chamada_grava, teste_repeticao_nao_duplica, teste_mesma_chave_para_outro_reembolso,
          teste_pedido_que_nao_existe, teste_valor_fora_do_pedido, teste_pedidos_intactos]

if __name__ == '__main__':
    falhas = 0
    for teste in TESTES:
        try:
            teste()
            print('ok   ', teste.__name__)
        except Exception as erro:  # o teste mostra qualquer erro, inclusive NotImplementedError
            falhas += 1
            print('FALHA', teste.__name__, '->', type(erro).__name__, erro)
    print(f'{len(TESTES) - falhas} de {len(TESTES)} testes passaram')
    sys.exit(1 if falhas else 0)
