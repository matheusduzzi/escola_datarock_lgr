"""Seus testes do retomar. Um teste por linha da tabela do exercício.

    python3 meus_testes.py                    testa retomar.py
    python3 meus_testes.py outra_copia.py     testa outro arquivo

Cada teste recebe o módulo do servidor em `m` e monta o próprio banco com m.Banco().
Para reiniciar o servidor, crie outro m.Atendimento com o mesmo banco. Olhe o banco
(banco.donos, contar_fotos, textos), não só o código que o retomar retorna.
O primeiro teste é um exemplo.
"""
import sys

from testes import DELA, DELE, RECUSA, contar_fotos, rodar_testes, textos  # noqa: F401


def teste_retoma_a_conversa_dela(m):
    at = m.Atendimento(m.Banco())
    t = at.nova_conversa(DELA)
    at.enviar(t, DELA, 'Quero saber do pedido 7')
    assert at.retomar(DELA) == t


TESTES = [teste_retoma_a_conversa_dela]

if __name__ == '__main__':
    sys.exit(rodar_testes(TESTES, sys.argv[1] if len(sys.argv) > 1 else 'retomar.py'))
