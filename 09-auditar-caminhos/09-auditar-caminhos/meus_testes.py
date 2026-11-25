"""Seus testes do exercício: a quinta reproduzida.

    python3 meus_testes.py                                   testa servidor.py com os arquivos de quinta
    python3 meus_testes.py servidor.py --trilha copia.jsonl  compara com outra trilha
    python3 meus_testes.py servidor.py --extrato copia.csv   compara com outro extrato

Cada teste recebe o módulo do servidor em `m` e monta o próprio banco e a própria operadora.
Leia os arquivos exportados só pelas constantes QUINTA e EXTRATO_QUINTA: as opções --trilha e
--extrato trocam o arquivo por trás delas. O primeiro teste é um exemplo.
"""
import sys

import testes
from testes import (ANA, BRUNO, DANIELA, DELA, DELE, Operadora, comparar, extrato, ler_extrato,  # noqa: F401
                    ler_trilha, por_pedido, relogio, rodar_testes, trilha_toda)

QUINTA = testes.QUINTA
EXTRATO_QUINTA = testes.EXTRATO_QUINTA


def teste_exemplo_o_29_comeca_igual(m):
    at = m.Atendimento(m.Banco(), Operadora())
    at.pedir_reembolso(DELA, 29)
    feito = por_pedido(trilha_toda(at))[29]
    exportado = por_pedido(ler_trilha(QUINTA))[29]
    assert feito == exportado[:len(feito)], (feito, exportado)


TESTES = [teste_exemplo_o_29_comeca_igual]


def trocar_arquivos(args):
    """As opções --trilha e --extrato trocam os arquivos lidos pelos testes."""
    global QUINTA, EXTRATO_QUINTA
    resto = list(args)
    for opcao in ('--trilha', '--extrato'):
        if opcao in resto:
            i = resto.index(opcao)
            if opcao == '--trilha':
                QUINTA = resto[i + 1]
            else:
                EXTRATO_QUINTA = resto[i + 1]
            del resto[i:i + 2]
    return resto


if __name__ == '__main__':
    resto = trocar_arquivos(sys.argv[1:])
    sys.exit(rodar_testes(TESTES, resto[0] if resto else 'servidor.py'))
