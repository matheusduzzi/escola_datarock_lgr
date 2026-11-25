"""Um nó que chama a operadora e cai depois de o dinheiro sair. Mostra quantas vezes ele roda.

    python3 queda.py                     sem chave
    python3 queda.py chave-nova          com uma chave nova a cada vez que o nó roda
    python3 queda.py chave-do-pedido     com a chave que sai do pedido
"""
import sys
import uuid
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from externos import ForaDoAr, Operadora

MODO = sys.argv[1] if len(sys.argv) > 1 else 'sem-chave'
assert MODO in ('sem-chave', 'chave-nova', 'chave-do-pedido'), MODO


class Estado(TypedDict, total=False):
    id_pedido: int
    status: str


operadora = Operadora()


def reembolsar(estado):
    print('   [nó reembolsar começou]')
    chave = {'sem-chave': None, 'chave-nova': f'estorno-{uuid.uuid4().hex[:6]}',
             'chave-do-pedido': f"estorno-{estado['id_pedido']}"}[MODO]
    if chave:
        print(f'   [chave: {chave}]' if MODO == 'chave-do-pedido' else '   [chave: uma nova]')
    operadora.estornar(estado['id_pedido'], 99.9, chave=chave)
    return {'status': 'reembolsado'}


g = StateGraph(Estado)
g.add_node('reembolsar', reembolsar)
g.add_edge(START, 'reembolsar')
g.add_edge('reembolsar', END)
grafo = g.compile(checkpointer=InMemorySaver())
config = {'configurable': {'thread_id': 'pedido-101'}}

print('1. primeira chamada; a operadora cai depois de estornar')
operadora.cair('depois')
try:
    grafo.invoke({'id_pedido': 101}, config)
except ForaDoAr as erro:
    print(f'   caiu: {erro}')
print(f"   próximo nó: {grafo.get_state(config).next}")
print(f'   estornos na operadora: {len(operadora.pagamentos)}')
print('2. retomada com invoke(None)')
final = grafo.invoke(None, config)
print(f"   status: {final['status']}")
print(f'   estornos na operadora: {len(operadora.pagamentos)}')
