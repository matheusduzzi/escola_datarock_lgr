"""A versão do grafo do pedido que um colega mandou para revisão.

    python3 versao_do_colega.py "O pedido 84 já foi enviado?"
    python3 testar_pedido.py versao_do_colega.py

Ela compila e roda sem erro. Ache a diferença para o pedido_grafo.py.
"""
import operator
import sys
from typing import Annotated, Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from atendimento_antigo import SistemaForaDoAr, numero_do_pedido, sistema_consultar
from modelo_falso import ModeloFalso


class Estado(TypedDict, total=False):
    mensagem: str
    numero: Optional[int]
    consulta: str  # achou, sem_numero, nao_achou ou falhou
    pedido: dict
    resposta: str
    caminho: Annotated[list, operator.add]


def ler_numero(estado):
    return {'numero': numero_do_pedido(estado.get('mensagem', '')), 'caminho': ['ler_numero']}


def instrucao_do_pedido(estado):
    """O que o nó redigir manda para o modelo. Só usa o que está no estado."""
    consulta = estado.get('consulta')
    if consulta == 'achou':
        p = estado['pedido']
        fato = (f"Pedido {p['id_pedido']}: {p['produto']}, status {p['status']}, "
                f"previsão de entrega {p['previsao_entrega']}.")
    elif consulta == 'sem_numero':
        fato = 'O cliente não mandou o número do pedido. Peça o número.'
    elif consulta == 'nao_achou':
        fato = f"O pedido {estado.get('numero')} não existe no sistema. Peça para o cliente ver o número."
    else:
        fato = 'O sistema de pedidos não respondeu. Diga que a equipe vai responder em seguida.'
    return f"Responda ao cliente da Loja Exemplo em uma frase. {fato} Mensagem do cliente: {estado.get('mensagem', '')}"


def montar_grafo(modelo, consultar_sistema=sistema_consultar):
    """O modelo e o sistema entram de fora: o teste passa um modelo falso e um sistema que falha."""

    def consultar(estado):
        numero = estado.get('numero')
        if numero is None:
            return {'consulta': 'sem_numero', 'caminho': ['consultar']}
        try:
            pedido = consultar_sistema(numero)
        except SistemaForaDoAr:
            return {'consulta': 'falhou', 'caminho': ['consultar']}
        if pedido is None:
            return {'consulta': 'nao_achou', 'caminho': ['consultar']}
        return {'consuta': 'achou', 'pedido': pedido, 'caminho': ['consultar']}

    def redigir(estado):
        return {'resposta': modelo.responder(instrucao_do_pedido(estado)), 'caminho': ['redigir']}

    g = StateGraph(Estado)
    g.add_node('ler_numero', ler_numero)
    g.add_node('consultar', consultar)
    g.add_node('redigir', redigir)
    g.add_edge(START, 'ler_numero')
    g.add_edge('ler_numero', 'consultar')
    g.add_edge('consultar', 'redigir')
    g.add_edge('redigir', END)
    return g.compile()


if __name__ == '__main__':
    mensagem = sys.argv[1] if len(sys.argv) > 1 else 'O pedido 84 já foi enviado?'
    modelo = ModeloFalso(['(resposta do modelo falso)'])
    final = montar_grafo(modelo).invoke({'mensagem': mensagem})
    print('caminho:', ' > '.join(final['caminho']))
    print('numero:', final.get('numero'), '| consulta:', final.get('consulta'))
    print('instrução para o modelo:', modelo.chamadas[0])
    print('resposta:', final['resposta'])
    print('chamadas ao modelo:', len(modelo.chamadas))
