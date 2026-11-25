"""Atendimento da Loja Exemplo com arestas condicionais.

Duas decisões viram aresta condicional:
- depois de classificar: para onde vai a mensagem (com saída para rota que não tem destino);
- depois de consultar o pedido: responder, pedir o número, tentar de novo ou passar para uma pessoa.

    python3 atendimento.py "O pedido 84 já foi enviado?"
"""
import operator
import sys
from typing import Annotated, Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from regras import classificar_texto, numero_do_pedido
from sistema import SistemaFora, SistemaPedidos

MAX_TENTATIVAS = 3
STATUS = {'aguardando_pagamento': 'aguardando pagamento', 'em_separacao': 'em separação',
          'enviado': 'enviado', 'entregue': 'entregue', 'cancelado': 'cancelado'}


class Estado(TypedDict, total=False):
    mensagem: str
    rota: str
    numero: Optional[int]
    consulta: str
    tentativas: int
    pedido: dict
    motivo: str
    atendido_por: str
    resposta: str
    caminho: Annotated[list, operator.add]


# Destinos de cada rota. A rota que não está aqui vai para "desconhecida".
DESTINOS = {'pedido': 'consultar', 'troca': 'troca', 'humano': 'humano', 'desconhecida': 'humano'}


def classificar(estado):
    texto = estado.get('mensagem', '')
    return {'rota': classificar_texto(texto), 'numero': numero_do_pedido(texto),
            'tentativas': 0, 'caminho': ['classificar']}


def escolher_rota(estado):
    """Só lê o estado. Rota sem destino vai para a saída de caso desconhecido."""
    rota = estado.get('rota')
    return rota if rota in DESTINOS else 'desconhecida'


def depois_da_consulta(estado):
    consulta = estado.get('consulta')
    if consulta == 'achou':
        return 'responder'
    if consulta == 'sem_numero':
        return 'pedir_numero'
    if consulta == 'falhou' and estado.get('tentativas', 0) < MAX_TENTATIVAS:
        return 'consultar'
    return 'humano'


def montar_grafo(sistema=None):
    sistema = sistema or SistemaPedidos()

    def consultar(estado):
        numero = estado.get('numero')
        if numero is None:
            return {'consulta': 'sem_numero', 'caminho': ['consultar']}
        try:
            pedido = sistema.buscar(numero)
        except SistemaFora:
            return {'consulta': 'falhou', 'tentativas': estado.get('tentativas', 0) + 1,
                    'caminho': ['consultar']}
        if pedido is None:
            return {'consulta': 'nao_achou', 'caminho': ['consultar']}
        return {'consulta': 'achou', 'pedido': pedido, 'caminho': ['consultar']}

    def responder(estado):
        p = estado['pedido']
        texto = (f"O pedido {p['id_pedido']} está {STATUS[p['status']]}. "
                 f"Previsão de entrega: {p['previsao_entrega']}.")
        return {'atendido_por': 'responder', 'resposta': texto, 'caminho': ['responder']}

    def pedir_numero(estado):
        return {'atendido_por': 'pedir_numero', 'resposta': 'Me passe o número do pedido, por favor.',
                'caminho': ['pedir_numero']}

    def troca(estado):
        return {'atendido_por': 'troca', 'resposta': 'Vou abrir a sua troca.', 'caminho': ['troca']}

    def humano(estado):
        rota = estado.get('rota')
        if rota not in DESTINOS:
            motivo = f'rota sem destino: {rota}'
        elif estado.get('consulta') == 'falhou':
            motivo = f"sistema de pedidos sem resposta em {estado.get('tentativas', 0)} tentativas"
        elif estado.get('consulta') == 'nao_achou':
            motivo = f"pedido {estado.get('numero')} não existe"
        else:
            motivo = 'mensagem sem assunto conhecido'
        return {'atendido_por': 'humano', 'motivo': motivo,
                'resposta': 'Vou passar para uma pessoa da equipe.', 'caminho': ['humano']}

    g = StateGraph(Estado)
    for nome, no in [('classificar', classificar), ('consultar', consultar), ('responder', responder),
                     ('pedir_numero', pedir_numero), ('troca', troca), ('humano', humano)]:
        g.add_node(nome, no)
    g.add_edge(START, 'classificar')
    g.add_conditional_edges('classificar', escolher_rota, DESTINOS)
    g.add_conditional_edges('consultar', depois_da_consulta, ['responder', 'pedir_numero', 'consultar', 'humano'])
    for nome in ('responder', 'pedir_numero', 'troca', 'humano'):
        g.add_edge(nome, END)
    return g.compile()


if __name__ == '__main__':
    mensagem = sys.argv[1] if len(sys.argv) > 1 else 'O pedido 84 já foi enviado?'
    final = montar_grafo().invoke({'mensagem': mensagem}, {'recursion_limit': 10})
    print('caminho:', ' > '.join(final['caminho']))
    print('resposta:', final['resposta'])
    if final.get('motivo'):
        print('motivo:', final['motivo'])
