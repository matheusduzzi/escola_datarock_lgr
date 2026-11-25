"""Aula 05. Checkpoints e identidade: a mesma conversa salva, sem e com o contrato.

    python3 demonstracao.py sem-contrato
    python3 demonstracao.py com-contrato

O atendimento tem um nó só, com regras fixas no lugar do modelo de linguagem. Sem rede e sem
chave. Os pedidos vêm de ../dados/loja/pedidos.csv.
"""
import csv
import re
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.runtime import Runtime

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


# Sem contrato: o cliente fica no estado, e o estado é salvo no checkpoint.
class EstadoComCliente(MessagesState):
    cliente: str


def montar_sem_contrato(checkpointer):
    def atender(estado):
        cliente = estado['cliente']  # o que ficou salvo, não quem está logado agora
        resposta = responder(estado['messages'][-1].content, estado['messages'][:-1], cliente)
        return {'messages': [('ai', resposta)]}

    g = StateGraph(EstadoComCliente)
    g.add_node('atender', atender)
    g.add_edge(START, 'atender')
    g.add_edge('atender', END)
    return g.compile(checkpointer=checkpointer)


# Com contrato: o cliente vem do login a cada chamada, pelo contexto, e não é salvo.
@dataclass
class Contexto:
    cliente: str


def montar_com_contrato(checkpointer):
    def atender(estado: MessagesState, runtime: Runtime[Contexto]):
        cliente = runtime.context.cliente  # quem está logado nessa chamada
        resposta = responder(estado['messages'][-1].content, estado['messages'][:-1], cliente)
        return {'messages': [('ai', resposta)]}

    g = StateGraph(MessagesState, context_schema=Contexto)
    g.add_node('atender', atender)
    g.add_edge(START, 'atender')
    g.add_edge('atender', END)
    return g.compile(checkpointer=checkpointer)


def config(thread_id):
    return {'configurable': {'thread_id': thread_id}}


def contar_checkpoints(grafo, thread_id):
    return len(list(grafo.get_state_history(config(thread_id))))


def falar(quem, texto, resposta):
    print(f'   {quem}: {texto}')
    print(f'   atendimento: {resposta}')


def sem_contrato():
    salvos = InMemorySaver()
    grafo = montar_sem_contrato(salvos)

    # A proposta do app: o código vai no link, e o cliente entra uma vez, quando a conversa abre.
    def enviar(thread_id, texto, cliente=None):
        entrada = {'messages': [('user', texto)]}
        if cliente is not None:
            entrada['cliente'] = cliente
        return grafo.invoke(entrada, config(thread_id))['messages'][-1].content

    print('1. A Cliente 0143 abre a conversa t-0143-a')
    texto = 'Quero saber do pedido 7'
    falar('Cliente 0143', texto, enviar('t-0143-a', texto, cliente='Cliente 0143'))
    print('2. O Cliente 0050, logado na conta dele, abre o link t-0143-a')
    for texto in ('Qual o valor do meu último pedido?', 'E o pedido 101?'):
        falar('Cliente 0050', texto, enviar('t-0143-a', texto))
    estado = grafo.get_state(config('t-0143-a')).values
    print(f"estado salvo em t-0143-a: {len(estado['messages'])} mensagens, cliente = {estado['cliente']}")
    print('checkpoints de t-0143-a:', contar_checkpoints(grafo, 't-0143-a'))
    print('3. O servidor reinicia, e o InMemorySaver começa vazio')
    depois = montar_sem_contrato(InMemorySaver())
    print('   mensagens em t-0143-a:', len(depois.get_state(config('t-0143-a')).values.get('messages', [])))


def com_contrato():
    salvos = InMemorySaver()
    grafo = montar_com_contrato(salvos)
    donos = {}  # na loja, uma tabela no mesmo banco das conversas

    def nova_conversa(cliente):
        thread_id = uuid.uuid4().hex  # o servidor cria o código; ninguém escolhe
        donos[thread_id] = cliente
        return thread_id

    def abrir(thread_id, cliente):
        # A porta: antes de carregar qualquer checkpoint, o dono da conversa é quem está logado?
        return donos.get(thread_id) == cliente

    def enviar(thread_id, texto, cliente):
        return grafo.invoke({'messages': [('user', texto)]}, config(thread_id),
                            context=Contexto(cliente=cliente))['messages'][-1].content

    print('1. A Cliente 0143 abre uma conversa nova; o servidor cria o código e anota a dona')
    dela = nova_conversa('Cliente 0143')
    texto = 'Quero saber do pedido 7'
    falar('Cliente 0143', texto, enviar(dela, texto, 'Cliente 0143'))
    antes = contar_checkpoints(grafo, dela)
    print('2. O Cliente 0050, logado na conta dele, abre o link da conversa da Cliente 0143')
    if abrir(dela, 'Cliente 0050'):
        conversa = dela
    else:
        conversa = nova_conversa('Cliente 0050')
        print('   porta: Não achei essa conversa na sua conta. Abri uma conversa nova para você.')
    print(f'   checkpoints da conversa da Cliente 0143: {contar_checkpoints(grafo, dela)} (antes: {antes})')
    for texto in ('Qual o valor do meu último pedido?', 'E o pedido 101?'):
        falar('Cliente 0050', texto, enviar(conversa, texto, 'Cliente 0050'))
    print('3. A Cliente 0143 volta à conversa dela')
    if abrir(dela, 'Cliente 0143'):
        texto = 'E o pedido 101?'
        falar('Cliente 0143', texto, enviar(dela, texto, 'Cliente 0143'))
    estado = grafo.get_state(config(dela)).values
    print(f"estado salvo na conversa da Cliente 0143: {len(estado['messages'])} mensagens, "
          f"chaves: {', '.join(estado)}")
    print('4. A Cliente 0143 pede para apagar a conversa')
    salvos.delete_thread(dela)
    del donos[dela]
    print('   checkpoints depois de apagar:', contar_checkpoints(grafo, dela))


if __name__ == '__main__':
    modo = sys.argv[1] if len(sys.argv) > 1 else ''
    if modo == 'sem-contrato':
        sem_contrato()
    elif modo == 'com-contrato':
        com_contrato()
    else:
        sys.exit('use: python3 demonstracao.py sem-contrato  ou  python3 demonstracao.py com-contrato')
