"""Aula 06. Memória por thread: o atendimento do jeito que estava no dia das duas reclamações.

Este arquivo não roda sozinho. Ele é usado pelo historia.py e pelos testes:

    python3 historia.py
    python3 testar_memoria.py

O atendimento tem um nó só, com regras fixas no lugar do modelo de linguagem. Sem rede e sem
chave. Os pedidos vêm de ../dados/loja/pedidos.csv.
"""
import csv
import re
from dataclasses import dataclass
from pathlib import Path

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.runtime import Runtime

RECUSA = 'Não achei essa conversa na sua conta.'

ARQUIVO = Path(__file__).resolve().parent.parent / 'dados' / 'loja' / 'pedidos.csv'
with open(ARQUIVO, encoding='utf-8') as f:
    PEDIDOS = {int(p['id_pedido']): p for p in csv.DictReader(f)}

SITUACAO = {'aguardando_pagamento': 'está aguardando pagamento', 'em_separacao': 'está em separação',
            'enviado': 'foi enviado', 'entregue': 'foi entregue', 'cancelado': 'foi cancelado'}


def reais(valor):
    return valor.replace('.', ',')


# A regra da aula 04: o pedido só aparece para quem é dono dele.
def consultar_pedido(numero, cliente):
    pedido = PEDIDOS.get(numero)
    if pedido is None or pedido['cliente'] != cliente:
        return 'Esse pedido não está no seu cadastro.'
    return (f"O pedido {numero}, {pedido['produto']}, {SITUACAO[pedido['status']]}. "
            f"Valor: {reais(pedido['valor'])}.")


def ultimo_pedido(cliente):
    numeros = [n for n, p in PEDIDOS.items() if p['cliente'] == cliente]
    return max(numeros) if numeros else None


# No lugar do modelo: ele lê a mensagem e o histórico, como um modelo de verdade leria.
def responder(texto, historico, cliente):
    numero = re.search(r'pedido (\d+)', texto)
    if numero:
        return consultar_pedido(int(numero.group(1)), cliente)
    if 'último pedido' in texto:
        for msg in reversed(historico):
            achou = re.search(r'O pedido (\d+),.*Valor: ([\d,]+)\.', msg.content)
            if msg.type == 'ai' and achou:
                return f'Pelo que conversamos, o seu último pedido é o {achou.group(1)}. Valor: {achou.group(2)}.'
        numero = ultimo_pedido(cliente)
        if numero is None:
            return 'Não achei pedidos no seu cadastro.'
        return 'Achei o seu último pedido. ' + consultar_pedido(numero, cliente)
    return 'Posso ajudar com os seus pedidos.'


# Quem está falando vem do login, em toda mensagem, pelo contexto (aula 05). Não fica salvo.
@dataclass
class Contexto:
    cliente: str


def montar_grafo(checkpointer):
    def atender(estado: MessagesState, runtime: Runtime[Contexto]):
        cliente = runtime.context.cliente
        resposta = responder(estado['messages'][-1].content, estado['messages'][:-1], cliente)
        return {'messages': [('ai', resposta)]}

    g = StateGraph(MessagesState, context_schema=Contexto)
    g.add_node('atender', atender)
    g.add_edge(START, 'atender')
    g.add_edge('atender', END)
    return g.compile(checkpointer=checkpointer)


def config(thread_id):
    return {'configurable': {'thread_id': thread_id}}


class Banco:
    """O banco do atendimento: as conversas salvas e a tabela de donos.

    No kit, o InMemorySaver faz o papel do banco. Reiniciar o servidor é criar um Atendimento
    novo com o mesmo Banco: o servidor novo encontra o banco como estava, como aconteceria com
    um banco de verdade, como o PostgresSaver.
    """

    def __init__(self):
        self.salvos = InMemorySaver()
        self.donos = {}  # thread_id -> cliente que abriu a conversa


class Atendimento:
    """O servidor do atendimento, versão do colega."""

    def __init__(self, banco):
        self.banco = banco
        self.grafo = montar_grafo(banco.salvos)
        self.proximo = 1  # o contador fica no processo

    def nova_conversa(self, cliente):
        thread_id = f't-{self.proximo}'
        self.proximo += 1
        self.banco.donos[thread_id] = cliente
        return thread_id

    def abrir(self, thread_id, cliente):
        """A porta: o dono da conversa é quem está logado?"""
        return self.banco.donos.get(thread_id) == cliente

    def enviar(self, thread_id, cliente, texto):
        # o app chama abrir() quando a conversa abre; aqui a conversa já está aberta
        final = self.grafo.invoke({'messages': [('user', texto)]}, config(thread_id),
                                  context=Contexto(cliente=cliente))
        return final['messages'][-1].content

    def apagar(self, thread_id, cliente):
        if not self.abrir(thread_id, cliente):
            return False
        self.banco.salvos.delete_thread(thread_id)
        del self.banco.donos[thread_id]
        return True
