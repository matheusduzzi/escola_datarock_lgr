"""Aula 09. Auditar caminhos: a versão do colega, com o caminho anotado no estado.

Este arquivo não roda sozinho. Ele é usado pelos scripts e pelos testes:

    python3 terca.py versao_do_colega.py
    python3 testar_trilha.py versao_do_colega.py

É o servidor da aula 08, com a chave do pedido e o registro de efeito. O colega acrescentou um
campo `caminho` no estado: cada nó põe o próprio nome nele quando termina, e o `trilha_de` lê
esse campo. Ele não tem o `incompletos` nem o `retomar_parados`.
Os pedidos vêm de ../dados/loja/pedidos.csv. Sem rede e sem chave de API.
"""
import csv
import operator
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from externos import ForaDoAr

LIMITE = 200.00  # "até 200,00" inclui os 200,00
FINANCEIRO = {'financeiro.ana', 'financeiro.bruno', 'financeiro.carla'}  # quem pode decidir
SO_FINANCEIRO = 'Só o financeiro decide reembolso.'
NADA_ESPERANDO = 'Esse reembolso não está esperando decisão.'
NADA_PARA_RETOMAR = 'Esse reembolso não está parado no meio.'
PEDIDO_DE_OUTRO = 'Esse pedido não está no seu cadastro.'

ARQUIVO = Path(__file__).resolve().parent.parent / 'dados' / 'loja' / 'pedidos.csv'
with open(ARQUIVO, encoding='utf-8') as f:
    PEDIDOS = {int(p['id_pedido']): p for p in csv.DictReader(f)}


def reais(valor):
    return f'{valor:.2f}'.replace('.', ',')


def agora():
    return datetime.now().astimezone().isoformat(timespec='seconds')


def chave_do_estorno(id_pedido):
    """A chave sai do pedido: é a mesma em toda tentativa e em todo pedido de reembolso dele."""
    return f'estorno-{id_pedido}'


class Estado(TypedDict, total=False):
    id_pedido: int
    cliente: str
    valor: float
    decisoes: list  # cada decisão de uma pessoa: resultado, quem e quando
    status: str  # 'reembolsado' ou 'rejeitado'; vazio enquanto espera ou está parado
    id_pagamento: str  # o código do estorno na operadora
    caminho: Annotated[list, operator.add]  # os nós por onde o reembolso passou


def montar_grafo(banco, operadora):
    def preparar(estado):
        return {'valor': float(PEDIDOS[estado['id_pedido']]['valor']), 'decisoes': [], 'caminho': ['preparar']}

    def precisa_aprovar(estado):
        return 'aprovar' if estado['valor'] > LIMITE else 'reembolsar'

    def aprovar(estado):
        # Nada de efeito antes do interrupt: na retomada, este nó roda de novo desde a primeira linha.
        resposta = interrupt({
            'id_pedido': estado['id_pedido'],
            'cliente': estado['cliente'],
            'valor': estado['valor'],
            'pergunta': f"Aprova o reembolso de {reais(estado['valor'])} do pedido {estado['id_pedido']}?",
        })
        aprovado = resposta.get('aprovado') is True  # só um True aprova
        decisao = {'resultado': 'aprovado' if aprovado else 'rejeitado',
                   'quem': resposta['quem'], 'quando': resposta['quando']}
        return {'decisoes': estado['decisoes'] + [decisao], 'caminho': ['aprovar']}

    def depois_da_decisao(estado):
        return 'reembolsar' if estado['decisoes'][-1]['resultado'] == 'aprovado' else 'rejeitar'

    def reembolsar(estado):
        # Este nó pode rodar mais de uma vez: depois de uma queda, o retomar começa por ele de novo.
        chave = chave_do_estorno(estado['id_pedido'])
        efeito = banco.efeitos.get(chave)
        if efeito and efeito['status'] == 'feito':  # já saiu: nem chama a operadora
            return {'status': 'reembolsado', 'id_pagamento': efeito['id_pagamento'], 'caminho': ['reembolsar']}
        tentativas = efeito['tentativas'] + 1 if efeito else 1
        banco.efeitos[chave] = {'status': 'enviado', 'id_pedido': estado['id_pedido'],  # anoto antes de chamar
                                'valor': estado['valor'], 'tentativas': tentativas, 'id_pagamento': ''}
        pagamento = operadora.estornar(estado['id_pedido'], estado['valor'], chave=chave)  # o efeito
        banco.efeitos[chave].update(status='feito', id_pagamento=pagamento['id_pagamento'])  # e depois
        return {'status': 'reembolsado', 'id_pagamento': pagamento['id_pagamento'], 'caminho': ['reembolsar']}

    def rejeitar(estado):
        return {'status': 'rejeitado', 'caminho': ['rejeitar']}

    g = StateGraph(Estado)
    g.add_node('preparar', preparar)
    g.add_node('aprovar', aprovar)
    g.add_node('reembolsar', reembolsar)
    g.add_node('rejeitar', rejeitar)
    g.add_edge(START, 'preparar')
    g.add_conditional_edges('preparar', precisa_aprovar, ['aprovar', 'reembolsar'])
    g.add_conditional_edges('aprovar', depois_da_decisao, ['reembolsar', 'rejeitar'])
    g.add_edge('reembolsar', END)
    g.add_edge('rejeitar', END)
    return g.compile(checkpointer=banco.salvos)


def config(thread_id):
    return {'configurable': {'thread_id': thread_id}}


class Banco:
    """O banco do atendimento: os reembolsos salvos, os donos e o registro de efeitos.

    No kit, o InMemorySaver faz o papel do banco. Reiniciar o servidor é criar um Atendimento
    novo com o mesmo Banco, como nas aulas 06 a 08.
    """

    def __init__(self):
        self.salvos = InMemorySaver()
        self.donos = {}  # thread_id -> cliente que pediu o reembolso
        self.efeitos = {}  # chave -> o que foi pedido lá fora e em que pé está ('enviado' ou 'feito')


class Atendimento:
    """O servidor do reembolso. Tudo o que ele precisa lembrar fica no banco."""

    def __init__(self, banco, operadora, relogio=agora):
        self.banco = banco
        self.operadora = operadora
        self.relogio = relogio  # a hora vem do servidor, não de quem decide
        self.grafo = montar_grafo(banco, operadora)

    def _rodar(self, entrada, thread_id):
        """Roda o grafo. Se a operadora cair, o reembolso fica parado no reembolsar, salvo no banco."""
        try:
            return self.grafo.invoke(entrada, config(thread_id))
        except ForaDoAr:
            return None

    def pedir_reembolso(self, cliente, id_pedido):
        """A cliente pede o reembolso de um pedido dela. Retorna o código do reembolso e a resposta."""
        pedido = PEDIDOS.get(id_pedido)
        if pedido is None or pedido['cliente'] != cliente:  # a regra da aula 04
            return None, PEDIDO_DE_OUTRO
        thread_id = uuid.uuid4().hex
        self.banco.donos[thread_id] = cliente
        final = self._rodar({'id_pedido': id_pedido, 'cliente': cliente}, thread_id)
        return thread_id, self._resposta(thread_id, final)

    def _resposta(self, thread_id, final):
        valores = self.grafo.get_state(config(thread_id)).values
        pedido, valor = valores['id_pedido'], reais(valores['valor'])
        if final is None:
            return f'A operadora não respondeu. O reembolso do pedido {pedido} ficou para retomar.'
        if '__interrupt__' in final:
            return f'O pedido {pedido} vale {valor}. O reembolso foi para o financeiro aprovar.'
        if final.get('status') == 'rejeitado':
            return f'Reembolso do pedido {pedido}: rejeitado.'
        return f'Reembolso de {valor} do pedido {pedido} feito.'

    def esperando(self, thread_id):
        """O reembolso está parado na pausa, esperando uma pessoa?"""
        return self.grafo.get_state(config(thread_id)).next == ('aprovar',)

    def parado(self, thread_id):
        """O reembolso caiu no meio do estorno e espera o retomar?"""
        return self.grafo.get_state(config(thread_id)).next == ('reembolsar',)

    def decidir(self, thread_id, quem, aprovado):
        """Uma pessoa do financeiro aprova (aprovado=True) ou rejeita o reembolso que está esperando."""
        if quem not in FINANCEIRO:
            return SO_FINANCEIRO
        if not self.esperando(thread_id):
            return NADA_ESPERANDO
        final = self._rodar(Command(resume={'aprovado': aprovado, 'quem': quem, 'quando': self.relogio()}),
                            thread_id)
        return self._resposta(thread_id, final)

    def retomar(self, thread_id):
        """Roda de novo o que ficou parado no meio. O grafo volta pelo reembolsar."""
        if not self.parado(thread_id):
            return NADA_PARA_RETOMAR
        return self._resposta(thread_id, self._rodar(None, thread_id))

    def parados(self):
        """Os reembolsos que caíram no meio, para retomar depois de um reinício."""
        return [t for t in self.banco.donos if self.parado(t)]

    def situacao(self, thread_id):
        """Para o financeiro e para os testes: status, decisões, se espera e se está parado."""
        valores = self.grafo.get_state(config(thread_id)).values
        return {'status': valores.get('status', ''), 'decisoes': valores.get('decisoes', []),
                'esperando': self.esperando(thread_id), 'parado': self.parado(thread_id)}

    def trilha_de(self, thread_id):
        """O caminho do reembolso, lido do estado salvo: um nó por passagem que terminou."""
        valores = self.grafo.get_state(config(thread_id)).values
        return [{'quando': '', 'thread': thread_id, 'pedido': valores.get('id_pedido'), 'onde': no,
                 'evento': 'terminou', 'detalhe': ''} for no in valores.get('caminho', [])]
