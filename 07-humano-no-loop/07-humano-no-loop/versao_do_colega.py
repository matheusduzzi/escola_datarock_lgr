"""Aula 07. Humano no loop: o servidor do reembolso do jeito que estava no dia das duas reclamações.

    python3 historia.py versao_do_colega.py
    python3 testar_aprovacao.py versao_do_colega.py

A regra do financeiro: reembolso até 200,00 sai direto; acima disso, uma pessoa do financeiro
aprova ou rejeita. Cada pedido de reembolso é um thread. Os pedidos vêm de
../dados/loja/pedidos.csv. Sem rede e sem chave.
"""
import csv
import uuid
from datetime import datetime
from pathlib import Path
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

LIMITE = 200.00  # "até 200,00" inclui os 200,00
FINANCEIRO = {'financeiro.ana', 'financeiro.bruno', 'financeiro.carla'}  # quem pode decidir
SO_FINANCEIRO = 'Só o financeiro decide reembolso.'
NADA_ESPERANDO = 'Esse reembolso não está esperando decisão.'
PEDIDO_DE_OUTRO = 'Esse pedido não está no seu cadastro.'

ARQUIVO = Path(__file__).resolve().parent.parent / 'dados' / 'loja' / 'pedidos.csv'
with open(ARQUIVO, encoding='utf-8') as f:
    PEDIDOS = {int(p['id_pedido']): p for p in csv.DictReader(f)}


def reais(valor):
    return f'{valor:.2f}'.replace('.', ',')


def agora():
    return datetime.now().astimezone().isoformat(timespec='seconds')


class Estado(TypedDict, total=False):
    id_pedido: int
    cliente: str
    valor: float
    status: str  # 'reembolsado' ou 'rejeitado'; vazio enquanto espera


def montar_grafo(banco):
    def preparar(estado):
        return {'valor': float(PEDIDOS[estado['id_pedido']]['valor'])}

    def precisa_aprovar(estado):
        return 'aprovar' if estado['valor'] > LIMITE else 'reembolsar'

    def aprovar(estado):
        pagamento = {'id_pedido': estado['id_pedido'], 'valor': estado['valor']}
        banco.pagamentos.append(pagamento)  # o estorno demora no banco: mando antes e cancelo se negarem
        resposta = interrupt({
            'id_pedido': estado['id_pedido'],
            'cliente': estado['cliente'],
            'valor': estado['valor'],
            'pergunta': f"Aprova o reembolso de {reais(estado['valor'])} do pedido {estado['id_pedido']}?",
        })
        if resposta.get('aprovado') is not True:
            banco.pagamentos.remove(pagamento)  # cancela o estorno
            return {'status': 'rejeitado'}
        return {'status': 'reembolsado'}

    def reembolsar(estado):
        banco.pagamentos.append({'id_pedido': estado['id_pedido'], 'valor': estado['valor']})
        return {'status': 'reembolsado'}

    g = StateGraph(Estado)
    g.add_node('preparar', preparar)
    g.add_node('aprovar', aprovar)
    g.add_node('reembolsar', reembolsar)
    g.add_edge(START, 'preparar')
    g.add_conditional_edges('preparar', precisa_aprovar, ['aprovar', 'reembolsar'])
    g.add_edge('aprovar', END)
    g.add_edge('reembolsar', END)
    return g.compile(checkpointer=banco.salvos)


def config(thread_id):
    return {'configurable': {'thread_id': thread_id}}


class Banco:
    """O banco do atendimento: os reembolsos salvos, a tabela de donos e os pagamentos feitos.

    No kit, o InMemorySaver faz o papel do banco. Reiniciar o servidor é criar um Atendimento
    novo com o mesmo Banco, como na aula 06.
    """

    def __init__(self):
        self.salvos = InMemorySaver()
        self.donos = {}  # thread_id -> cliente que pediu o reembolso
        self.pagamentos = []  # um item por reembolso pago: é o dinheiro saindo


class Atendimento:
    """O servidor do reembolso. Tudo o que ele precisa lembrar fica no banco."""

    def __init__(self, banco, relogio=agora):
        self.banco = banco
        self.relogio = relogio  # a hora vem do servidor, não de quem decide
        self.grafo = montar_grafo(banco)

    def pedir_reembolso(self, cliente, id_pedido):
        """A cliente pede o reembolso de um pedido dela. Retorna o código do reembolso e a resposta."""
        pedido = PEDIDOS.get(id_pedido)
        if pedido is None or pedido['cliente'] != cliente:  # a regra da aula 04
            return None, PEDIDO_DE_OUTRO
        thread_id = uuid.uuid4().hex
        self.banco.donos[thread_id] = cliente
        final = self.grafo.invoke({'id_pedido': id_pedido, 'cliente': cliente}, config(thread_id))
        valor = reais(final['valor'])
        if '__interrupt__' in final:
            return thread_id, f'O pedido {id_pedido} vale {valor}. O reembolso foi para o financeiro aprovar.'
        return thread_id, f'Reembolso de {valor} do pedido {id_pedido} feito.'

    def esperando(self, thread_id):
        """O reembolso está parado na pausa, esperando uma pessoa?"""
        return self.grafo.get_state(config(thread_id)).next == ('aprovar',)

    def decidir(self, thread_id, quem, aprovado):
        """Uma pessoa do financeiro aprova (aprovado=True) ou rejeita o reembolso que está esperando."""
        if quem not in FINANCEIRO:  # a porta do financeiro: nem a própria cliente decide
            return SO_FINANCEIRO
        if not self.esperando(thread_id):  # já decidido, automático ou inexistente
            return NADA_ESPERANDO
        final = self.grafo.invoke(Command(resume={'aprovado': aprovado}), config(thread_id))
        return f"Reembolso do pedido {final['id_pedido']}: {final.get('status') or 'esperando'}."

    def situacao(self, thread_id):
        """Para o financeiro e para os testes: status, decisões e se ainda espera."""
        valores = self.grafo.get_state(config(thread_id)).values
        return {'status': valores.get('status', ''), 'decisoes': valores.get('decisoes', []),
                'esperando': self.esperando(thread_id)}
