"""Seus testes da troca. Um teste por linha da tabela do exercício.

    python3 meus_testes.py                    testa troca.py
    python3 meus_testes.py outra_copia.py     testa outro arquivo

Cada teste recebe o módulo do atendimento em `m`. Use conversar(m, cliente, mensagem) para passar
pelo modelo e decidir_na_mao(m, cliente, 'abrir_troca', args) para mandar uma decisão escrita na
mão. Olhe sempre sistema.efeitos. O primeiro teste é um exemplo.
"""
import sys

from testes import conversar, decidir_na_mao, rodar_testes, schema_do_modelo  # noqa: F401

CLIENTE = 'Cliente 0143'  # pedidos 7 (entregue) e 101 (enviado)


def teste_cancelamento_continua_igual(m):
    resposta, sistema = conversar(m, 'Cliente 0036', 'Quero cancelar o pedido 40')
    assert sistema.efeitos == [('cancelar', 40)], sistema.efeitos


TESTES = [teste_cancelamento_continua_igual]

if __name__ == '__main__':
    sys.exit(rodar_testes(TESTES, sys.argv[1] if len(sys.argv) > 1 else 'troca.py'))
