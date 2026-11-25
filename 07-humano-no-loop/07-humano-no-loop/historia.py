"""As duas reclamações do financeiro, rodadas contra um servidor.

    python3 historia.py                       com servidor.py
    python3 historia.py versao_do_colega.py   com a versão do colega
"""
import sys

from testes import ANA, BRUNO, DELA, DELE, carregar

HORAS = iter(['2026-11-13T15:40:00-03:00', '2026-11-13T16:05:00-03:00'])


def lista(pagamentos, reais):
    return ', '.join(f"{p['id_pedido']} ({reais(p['valor'])})" for p in pagamentos) or 'nenhum'


def dinheiro(m):
    print('1. Dois reembolsos acima de 200,00, decididos depois de um reinício')
    banco = m.Banco()
    manha = m.Atendimento(banco)
    codigos = {}
    for cliente, pedido in ((DELA, 29), (DELE, 44)):
        print(f'   {cliente} pede o reembolso do pedido {pedido}')
        codigos[pedido], resposta = manha.pedir_reembolso(cliente, pedido)
        print(f'   atendimento: {resposta}')
    print(f'   pagamentos enquanto os dois esperam: {lista(banco.pagamentos, m.reais)}')
    tarde = m.Atendimento(banco, relogio=lambda: next(HORAS))
    print('   o servidor reinicia; o banco continua com os reembolsos parados')
    print(f'   {ANA} rejeita o pedido 29: {tarde.decidir(codigos[29], ANA, False)}')
    print(f'   {BRUNO} aprova o pedido 44: {tarde.decidir(codigos[44], BRUNO, True)}')
    print(f'   pagamentos no fim: {lista(banco.pagamentos, m.reais)}')
    return tarde, codigos


def quem_decidiu(tarde, codigos):
    print('2. Quem decidiu, e quando')
    for pedido, t in codigos.items():
        s = tarde.situacao(t)
        anotadas = [f"{d['resultado']} por {d['quem']} em {d['quando']}" for d in s['decisoes']]
        print(f"   pedido {pedido}: {s['status']}; decisões anotadas: {'; '.join(anotadas) or 'nenhuma'}")


if __name__ == '__main__':
    m = carregar(sys.argv[1] if len(sys.argv) > 1 else 'servidor.py')
    quem_decidiu(*dinheiro(m))
