"""A queda da operadora no meio do estorno, rodada contra um servidor.

    python3 historia.py                       com servidor.py
    python3 historia.py versao_do_colega.py   com a versão do colega
"""
import sys

from testes import ANA, DELA, DELE, LUMINARIA, Operadora, carregar, relogio


def lista(pagamentos, reais):
    return ', '.join(f"{p['id_pedido']} ({reais(p['valor'])})" for p in pagamentos) or 'nenhum'


def queda(m):
    print('1. A operadora cai no meio de dois estornos; o servidor reinicia e retoma')
    banco, op = m.Banco(), Operadora()
    manha = m.Atendimento(banco, op, relogio('2026-11-25T10:12:00-03:00'))
    op.cair('depois')
    print(f'   {LUMINARIA} pede o reembolso do pedido 101')
    luminaria, resposta = manha.pedir_reembolso(LUMINARIA, 101)
    print(f'   atendimento: {resposta}')
    tenis, _ = manha.pedir_reembolso(DELA, 29)
    op.cair('antes')
    print(f'   {ANA} aprova o pedido 29: {manha.decidir(tenis, ANA, True)}')
    print(f'   estornos na operadora antes de retomar: {lista(op.pagamentos, m.reais)}')
    tarde = m.Atendimento(banco, op)
    print('   o servidor reinicia; o banco continua com os reembolsos parados')
    for t in tarde.parados():
        print(f'   retomar: {tarde.retomar(t)}')
    print(f'   estornos na operadora no fim: {lista(op.pagamentos, m.reais)}')
    registro = getattr(banco, 'efeitos', None)
    if registro is None:
        print('   registro dos estornos: nenhum')
    for chave, e in (registro or {}).items():
        print(f"   registro {chave}: {e['status']}, {e['tentativas']} tentativas, estorno {e['id_pagamento']}")


def clique_duplo(m):
    print('2. A cliente pede o reembolso do mesmo pedido duas vezes')
    op = Operadora()
    at = m.Atendimento(m.Banco(), op)
    primeiro, _ = at.pedir_reembolso(DELE, 44)
    segundo, _ = at.pedir_reembolso(DELE, 44)
    print(f'   {ANA} aprova o primeiro: {at.decidir(primeiro, ANA, True)}')
    print(f"   financeiro.bruno aprova o segundo: {at.decidir(segundo, 'financeiro.bruno', True)}")
    print(f'   estornos na operadora: {lista(op.pagamentos, m.reais)}')


if __name__ == '__main__':
    m = carregar(sys.argv[1] if len(sys.argv) > 1 else 'servidor.py')
    queda(m)
    clique_duplo(m)
