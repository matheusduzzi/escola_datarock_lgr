"""Seus testes do aviso para a cliente. Um teste por linha da tabela do exercício.

    python3 meus_testes.py                    testa aviso.py
    python3 meus_testes.py outra_copia.py     testa outro arquivo

Cada teste recebe o módulo do servidor em `m` e monta o próprio banco, a própria operadora e o
próprio envio de mensagens. Para reiniciar o servidor, crie outro m.Atendimento com o mesmo
banco, a mesma operadora e o mesmo mensageiro: os dois serviços são de fora e não reiniciam.
Olhe os serviços (pagos, enviadas) e o banco.efeitos, não só o texto que o servidor retorna.
O primeiro teste é um exemplo.
"""
import sys

from testes import ANA, BRUNO, DELA, DELE, LUMINARIA, Mensageiro, Operadora, enviadas, pagos, relogio, rodar_testes  # noqa: F401


def teste_reembolso_pago_avisa_uma_vez(m):
    banco, op, msg = m.Banco(), Operadora(), Mensageiro()
    at = m.Atendimento(banco, op, mensageiro=msg)
    at.pedir_reembolso(LUMINARIA, 101)  # 99,90: sai sem aprovação
    assert pagos(op, 101) == 1, op.pagamentos
    assert enviadas(msg, LUMINARIA) == 1, msg.mensagens


TESTES = [teste_reembolso_pago_avisa_uma_vez]

if __name__ == '__main__':
    sys.exit(rodar_testes(TESTES, sys.argv[1] if len(sys.argv) > 1 else 'aviso.py'))
