"""Seus testes do cancelamento. Um teste por caminho, mais o caso desconhecido.

    python3 meus_testes.py                    testa cancelamento.py
    python3 meus_testes.py outra_copia.py     testa outro arquivo com montar_grafo

Cada teste recebe o módulo do grafo em `m`. Use rodar(m, mensagem) ou rodar(m, mensagem, falhas=...)
e confira o caminho inteiro, não só quem atendeu. O primeiro teste é um exemplo.
"""
import sys

from testes import rodar, rodar_testes


def teste_pedido_continua_igual(m):
    final, _ = rodar(m, 'O pedido 84 já foi enviado?')
    assert final['caminho'] == ['classificar', 'consultar', 'responder'], final['caminho']


TESTES = [teste_pedido_continua_igual]

if __name__ == '__main__':
    sys.exit(rodar_testes(TESTES, sys.argv[1] if len(sys.argv) > 1 else 'cancelamento.py'))
