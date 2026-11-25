"""Um nó que pausa antes do reembolso, com um print no começo para ver quando ele roda.

    python3 pausa.py            a pausa e a retomada
    python3 pausa.py engolida   o mesmo nó com o interrupt dentro de um try/except
"""
import sys
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class Estado(TypedDict, total=False):
    id_pedido: int
    status: str


def aprovar(estado):
    print('   [nó aprovar começou]')
    resposta = interrupt({'id_pedido': estado['id_pedido'], 'pergunta': 'Aprova o reembolso?'})
    print(f'   [o financeiro respondeu: {resposta!r}]')
    return {'status': 'reembolsado' if resposta is True else 'rejeitado'}


def aprovar_engolida(estado):
    print('   [nó aprovar começou]')
    try:
        resposta = interrupt({'id_pedido': estado['id_pedido'], 'pergunta': 'Aprova o reembolso?'})
    except Exception as erro:  # pega também a pausa
        print(f'   [o except pegou: {type(erro).__name__}]')
        resposta = None
    return {'status': 'reembolsado' if resposta is True else 'rejeitado'}


engolida = sys.argv[1:] == ['engolida']
g = StateGraph(Estado)
g.add_node('aprovar', aprovar_engolida if engolida else aprovar)
g.add_edge(START, 'aprovar')
g.add_edge('aprovar', END)
grafo = g.compile(checkpointer=InMemorySaver())
config = {'configurable': {'thread_id': 'reembolso-29'}}

print('1. primeira chamada')
primeira = grafo.invoke({'id_pedido': 29}, config)
if '__interrupt__' in primeira:
    print('   pausou com:', primeira['__interrupt__'][0].value)
print('   próximo nó:', grafo.get_state(config).next)
if engolida:
    print('   status:', primeira['status'])
    sys.exit()
print('2. retomada')
final = grafo.invoke(Command(resume=True), config)
print('   status:', final['status'])
