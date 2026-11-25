"""Atendimento da Loja Exemplo: a versão que o colega quer ligar.

O mesmo grafo do atendimento.py, com duas linhas diferentes: a aprovação e a chamada ao
sistema de pagamentos. O colega diz que ela passou no reembolso normal.

    python3 versao_do_colega.py "Cliente 0098" "Quero o reembolso do pedido 52"
"""
import operator
import sys
from typing import Annotated, Optional, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from pagamentos import Pagamentos
from regras import classificar_texto, numero_do_pedido
from sistema import SistemaFora, SistemaPedidos

MAX_TENTATIVAS = 3
LIMITE = 200.00  # até 200 reais, inclusive, o atendimento reembolsa sem aprovação
PAGOS = ('em_separacao', 'enviado', 'entregue')  # pedidos com pagamento para devolver
STATUS = {'aguardando_pagamento': 'aguardando pagamento', 'em_separacao': 'em separação',
          'enviado': 'enviado', 'entregue': 'entregue', 'cancelado': 'cancelado'}


class Estado(TypedDict, total=False):
    mensagem: str
    cliente: str  # quem está logado na conversa; vem do aplicativo, não da mensagem
    rota: str
    numero: Optional[int]
    consulta: Optional[str]
    tentativas: int
    pedido: Optional[dict]
    valido: Optional[bool]
    valor: Optional[float]
    chave: Optional[str]
    decisao: Optional[str]
    motivo: Optional[str]
    atendido_por: Optional[str]
    resposta: Optional[str]
    caminho: Annotated[list, operator.add]


DESTINOS = {'pedido': 'consultar', 'troca': 'troca', 'reembolso': 'consultar',
            'humano': 'humano', 'desconhecida': 'humano'}


def reais(valor):
    return f'R$ {valor:.2f}'.replace('.', ',')


def classificar(estado):
    """Decide a rota e limpa o que sobrou da mensagem anterior na mesma conversa."""
    texto = estado.get('mensagem', '')
    return {'rota': classificar_texto(texto), 'numero': numero_do_pedido(texto), 'tentativas': 0,
            'consulta': None, 'pedido': None, 'valido': None, 'valor': None, 'chave': None,
            'decisao': None, 'motivo': None, 'atendido_por': None, 'resposta': None,
            'caminho': ['classificar']}


def escolher_rota(estado):
    rota = estado.get('rota')
    return rota if rota in DESTINOS else 'desconhecida'


def depois_da_consulta(estado):
    consulta = estado.get('consulta')
    if consulta == 'achou':
        return 'validar' if estado.get('rota') == 'reembolso' else 'responder'
    if consulta == 'sem_numero':
        return 'pedir_numero'
    if consulta == 'falhou' and estado.get('tentativas', 0) < MAX_TENTATIVAS:
        return 'consultar'
    return 'humano'


def validar(estado):
    """Valida o reembolso antes de qualquer efeito. Não chama o sistema de pagamentos."""
    p = estado['pedido']
    n = p['id_pedido']
    if p['cliente'] != estado.get('cliente'):
        return {'valido': False, 'motivo': f'pedido {n} é de outro cliente', 'caminho': ['validar']}
    if p['status'] not in PAGOS:
        return {'valido': False, 'motivo': f"pedido {n} está {STATUS[p['status']]}: não há pagamento para devolver",
                'caminho': ['validar']}
    return {'valido': True, 'valor': float(p['valor']), 'chave': f'reembolso-pedido-{n}', 'caminho': ['validar']}


def depois_de_validar(estado):
    if not estado.get('valido'):
        return 'humano'
    return 'reembolsar' if estado['valor'] <= LIMITE else 'aprovar'


def aprovar(estado):
    # Nada com efeito antes do interrupt: na retomada, esse nó roda de novo desde o começo.
    resposta = interrupt({'pedido': int(estado['pedido']['id_pedido']), 'valor': estado['valor'],
                          'pergunta': 'Aprova o reembolso?'})
    return {'decisao': 'aprovado' if resposta else 'negado', 'caminho': ['aprovar']}


def depois_da_aprovacao(estado):
    return 'reembolsar' if estado.get('decisao') == 'aprovado' else 'negar'


def montar_grafo(sistema=None, pagamentos=None, checkpointer=None):
    sistema = sistema or SistemaPedidos()
    pagamentos = pagamentos or Pagamentos()

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

    def reembolsar(estado):
        # O único nó com efeito.
        n = estado['pedido']['id_pedido']
        feito = pagamentos.reembolsar(None, int(n), estado['valor'])
        return {'atendido_por': 'reembolsar', 'caminho': ['reembolsar'],
                'resposta': f"Reembolso de {reais(estado['valor'])} do pedido {n} feito. "
                            f"Comprovante {feito['comprovante']}."}

    def negar(estado):
        n = estado['pedido']['id_pedido']
        return {'atendido_por': 'negar', 'motivo': 'o financeiro não aprovou', 'caminho': ['negar'],
                'resposta': f'O reembolso do pedido {n} não foi aprovado. Uma pessoa da equipe vai falar com você.'}

    def humano(estado):
        rota = estado.get('rota')
        if estado.get('motivo'):
            motivo = estado['motivo']
        elif rota not in DESTINOS:
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
                     ('pedir_numero', pedir_numero), ('troca', troca), ('validar', validar),
                     ('aprovar', aprovar), ('reembolsar', reembolsar), ('negar', negar), ('humano', humano)]:
        g.add_node(nome, no)
    g.add_edge(START, 'classificar')
    g.add_conditional_edges('classificar', escolher_rota, DESTINOS)
    g.add_conditional_edges('consultar', depois_da_consulta,
                            ['responder', 'validar', 'pedir_numero', 'consultar', 'humano'])
    g.add_conditional_edges('validar', depois_de_validar, ['humano', 'reembolsar', 'aprovar'])
    g.add_conditional_edges('aprovar', depois_da_aprovacao, ['reembolsar', 'negar'])
    for nome in ('responder', 'pedir_numero', 'troca', 'reembolsar', 'negar', 'humano'):
        g.add_edge(nome, END)
    return g.compile(checkpointer=checkpointer or InMemorySaver())


if __name__ == '__main__':
    cliente = sys.argv[1] if len(sys.argv) > 2 else 'Cliente 0259'
    mensagem = sys.argv[2] if len(sys.argv) > 2 else 'O pedido 84 já foi enviado?'
    config = {'configurable': {'thread_id': 'linha-de-comando'}, 'recursion_limit': 10}
    final = montar_grafo().invoke({'mensagem': mensagem, 'cliente': cliente}, config)
    print('caminho:', ' > '.join(final['caminho']))
    if '__interrupt__' in final:
        print('pausou para o financeiro:', final['__interrupt__'][0].value)
    else:
        print('resposta:', final['resposta'])
    if final.get('motivo'):
        print('motivo:', final['motivo'])
