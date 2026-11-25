"""Seus testes da regra das duas pessoas. Um teste por linha da tabela do exercício.

    python3 meus_testes.py                    testa dupla.py
    python3 meus_testes.py outra_copia.py     testa outro arquivo

Cada teste recebe o módulo do servidor em `m` e monta o próprio banco com m.Banco().
Para reiniciar o servidor, crie outro m.Atendimento com o mesmo banco. Olhe o banco
(pagos, situacao), não só o texto que o decidir retorna.
O primeiro teste é um exemplo.
"""
import sys

from testes import ANA, BRUNO, NOVE_HORAS, TARDE, pagos, relogio, rodar_testes  # noqa: F401

DELA = 'Cliente 0143'  # pedido 7, Cadeira de escritório, 850,00


def teste_de_200_a_500_continua_com_uma_aprovacao(m):
    banco = m.Banco()
    at = m.Atendimento(banco)
    t, _ = at.pedir_reembolso('Cliente 0198', 29)  # 349,90
    at.decidir(t, ANA, True)
    assert at.situacao(t)['status'] == 'reembolsado', at.situacao(t)
    assert pagos(banco, 29) == 1, banco.pagamentos


TESTES = [teste_de_200_a_500_continua_com_uma_aprovacao]

if __name__ == '__main__':
    sys.exit(rodar_testes(TESTES, sys.argv[1] if len(sys.argv) > 1 else 'dupla.py'))
