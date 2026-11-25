"""Aula 09. Auditar caminhos: o reembolso da aula 08 com a trilha de cada passagem.

Este arquivo não roda sozinho. Ele é usado pelos scripts e pelos testes da aula:

    python3 terca.py
    python3 testar_trilha.py

O grafo e o estorno são os da aula 08: até 200,00 o reembolso sai direto; acima disso, o
financeiro aprova ou rejeita; o estorno vai com a chave do pedido e o banco anota o efeito.
O que muda: cada nó anota no banco quando começa, termina, pausa ou cai, e o servidor anota o
que acontece fora do grafo (o pedido, a decisão, a decisão recusada, o retomar, a resposta).
O `incompletos` diz onde cada reembolso parado está e por quê. O `retomar_parados` é o retomar
da noite: só roda de novo o que caiu por queda, e um erro num reembolso não para os outros.
Os pedidos vêm de ../dados/loja/pedidos.csv. Sem rede e sem chave de API.
"""
import csv
import uuid
from datetime import datetime
from pathlib import Path
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import GraphInterrupt
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


def resumo(nome, saida):
    """O que vale anotar quando um nó termina."""
    if nome == 'preparar':
        return f"valor {reais(saida['valor'])}"
    if nome == 'aprovar':
        d = saida['decisoes'][-1]
        return f"{d['resultado']} por {d['quem']}"
    if nome == 'reembolsar':
        return f"estorno {saida['id_pagamento']}"
    return saida.get('status', '')


def montar_grafo(banco, operadora, relogio):
    def anotado(nome, no):
        """Embrulha um nó: anota quando ele começa, termina, pausa ou cai. O nó não muda."""
        def rodar(estado, config):
            t = config['configurable']['thread_id']
            banco.anotar(relogio(), t, nome, 'começou')
            try:
                saida = no(estado)
            except GraphInterrupt:  # o interrupt da pausa também sai do nó por uma exceção
                banco.anotar(relogio(), t, nome, 'pausou', 'esperando o financeiro')
                raise
            except Exception as erro:
                banco.anotar(relogio(), t, nome, 'caiu', f'{type(erro).__name__}: {erro}')
                raise
            banco.anotar(relogio(), t, nome, 'terminou', resumo(nome, saida))
            return saida
        return rodar

    def preparar(estado):
        return {'valor': float(PEDIDOS[estado['id_pedido']]['valor']), 'decisoes': []}

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
        return {'decisoes': estado['decisoes'] + [decisao]}

    def depois_da_decisao(estado):
        return 'reembolsar' if estado['decisoes'][-1]['resultado'] == 'aprovado' else 'rejeitar'

    def reembolsar(estado):
        # Este nó pode rodar mais de uma vez: depois de uma queda, o retomar começa por ele de novo.
        chave = chave_do_estorno(estado['id_pedido'])
        efeito = banco.efeitos.get(chave)
        if efeito and efeito['status'] == 'feito':  # já saiu: nem chama a operadora
            return {'status': 'reembolsado', 'id_pagamento': efeito['id_pagamento']}
        tentativas = efeito['tentativas'] + 1 if efeito else 1
        banco.efeitos[chave] = {'status': 'enviado', 'id_pedido': estado['id_pedido'],
                                'valor': estado['valor'], 'tentativas': tentativas, 'id_pagamento': ''}
        pagamento = operadora.estornar(estado['id_pedido'], estado['valor'], chave=chave)
        banco.efeitos[chave].update(status='feito', id_pagamento=pagamento['id_pagamento'])
        return {'status': 'reembolsado', 'id_pagamento': pagamento['id_pagamento']}

    def rejeitar(estado):
        return {'status': 'rejeitado'}

    g = StateGraph(Estado)
    for nome, no in [('preparar', preparar), ('aprovar', aprovar), ('reembolsar', reembolsar),
                     ('rejeitar', rejeitar)]:
        g.add_node(nome, anotado(nome, no))
    g.add_edge(START, 'preparar')
    g.add_conditional_edges('preparar', precisa_aprovar, ['aprovar', 'reembolsar'])
    g.add_conditional_edges('aprovar', depois_da_decisao, ['reembolsar', 'rejeitar'])
    g.add_edge('reembolsar', END)
    g.add_edge('rejeitar', END)
    return g.compile(checkpointer=banco.salvos)


def config(thread_id):
    return {'configurable': {'thread_id': thread_id}}


class Banco:
    """O banco do atendimento: os reembolsos salvos, os donos, o registro de efeitos e a trilha.

    No kit, o InMemorySaver faz o papel do banco. Reiniciar o servidor é criar um Atendimento
    novo com o mesmo Banco, como nas aulas 06 a 08.
    """

    def __init__(self):
        self.salvos = InMemorySaver()
        self.donos = {}  # thread_id -> cliente que pediu o reembolso
        self.pedidos = {}  # thread_id -> número do pedido
        self.efeitos = {}  # chave -> o que foi pedido lá fora e em que pé está ('enviado' ou 'feito')
        self.trilha = []  # uma linha por passagem: quando, thread, pedido, onde, evento, detalhe

    def anotar(self, quando, thread_id, onde, evento, detalhe=''):
        self.trilha.append({'quando': quando, 'thread': thread_id, 'pedido': self.pedidos.get(thread_id),
                            'onde': onde, 'evento': evento, 'detalhe': detalhe})


class Atendimento:
    """O servidor do reembolso. Tudo o que ele precisa lembrar fica no banco."""

    def __init__(self, banco, operadora, relogio=agora):
        self.banco = banco
        self.operadora = operadora
        self.relogio = relogio  # a hora vem do servidor, não de quem decide
        self.grafo = montar_grafo(banco, operadora, relogio)

    def _anotar(self, thread_id, evento, detalhe=''):
        self.banco.anotar(self.relogio(), thread_id, 'servidor', evento, detalhe)

    def _rodar(self, entrada, thread_id):
        """Roda o grafo. Se a operadora cair, o reembolso fica parado no reembolsar, salvo no banco."""
        try:
            return self.grafo.invoke(entrada, config(thread_id))
        except ForaDoAr:
            return None

    def _responder(self, thread_id, final):
        resposta = self._resposta(thread_id, final)
        self._anotar(thread_id, 'respondeu', resposta)
        return resposta

    def pedir_reembolso(self, cliente, id_pedido):
        """A cliente pede o reembolso de um pedido dela. Retorna o código do reembolso e a resposta."""
        pedido = PEDIDOS.get(id_pedido)
        if pedido is None or pedido['cliente'] != cliente:  # a regra da aula 04
            return None, PEDIDO_DE_OUTRO
        thread_id = uuid.uuid4().hex
        self.banco.donos[thread_id] = cliente
        self.banco.pedidos[thread_id] = id_pedido
        self._anotar(thread_id, 'pedido', cliente)
        final = self._rodar({'id_pedido': id_pedido, 'cliente': cliente}, thread_id)
        return thread_id, self._responder(thread_id, final)

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
            self._anotar(thread_id, 'decisão recusada', f'{quem}: {SO_FINANCEIRO}')
            return SO_FINANCEIRO
        if not self.esperando(thread_id):
            self._anotar(thread_id, 'decisão recusada', f'{quem}: {NADA_ESPERANDO}')
            return NADA_ESPERANDO
        self._anotar(thread_id, 'decisão', f"{quem}: {'aprovou' if aprovado is True else 'não aprovou'}")
        final = self._rodar(Command(resume={'aprovado': aprovado, 'quem': quem, 'quando': self.relogio()}),
                            thread_id)
        return self._responder(thread_id, final)

    def retomar(self, thread_id):
        """Roda de novo o que ficou parado no meio. O grafo volta pelo reembolsar."""
        if not self.parado(thread_id):
            self._anotar(thread_id, 'retomar recusado', NADA_PARA_RETOMAR)
            return NADA_PARA_RETOMAR
        self._anotar(thread_id, 'retomar')
        return self._responder(thread_id, self._rodar(None, thread_id))

    def parados(self):
        """Os reembolsos que caíram no meio do estorno, por qualquer motivo."""
        return [t for t in self.banco.donos if self.parado(t)]

    def trilha_de(self, thread_id):
        """A trilha de um reembolso, na ordem em que aconteceu."""
        return [e for e in self.banco.trilha if e['thread'] == thread_id]

    def ultima_queda(self, thread_id):
        """O último 'caiu' de um nó desse reembolso, ou None."""
        quedas = [e for e in self.trilha_de(thread_id) if e['evento'] == 'caiu']
        return quedas[-1] if quedas else None

    def incompletos(self):
        """Os reembolsos que não terminaram: onde cada um parou, por quê e o último passo."""
        lista = []
        for t in self.banco.donos:
            proximo = self.grafo.get_state(config(t)).next
            if not proximo:
                continue  # terminou: reembolsado ou rejeitado
            queda = self.ultima_queda(t)
            if proximo == ('aprovar',) and queda is None:
                motivo = 'esperando decisão do financeiro'
            elif queda and queda['detalhe'].startswith('ForaDoAr'):
                motivo = 'a operadora caiu: o retomar da noite tenta de novo'
            else:
                motivo = f"erro: {queda['detalhe'] if queda else 'sem anotação'}; precisa de uma pessoa"
            lista.append({'thread': t, 'pedido': self.banco.pedidos[t], 'onde': proximo[0],
                          'motivo': motivo, 'ultimo': self.trilha_de(t)[-1]})
        return lista

    def retomar_parados(self):
        """O retomar da noite. Só roda de novo o que caiu por queda; um erro num não para os outros."""
        for t in self.parados():
            queda = self.ultima_queda(t)
            if queda is None or not queda['detalhe'].startswith('ForaDoAr'):
                continue  # erro que não é queda: tentar de novo dá o mesmo erro; fica para uma pessoa
            try:
                self.retomar(t)
            except Exception as erro:  # o nó já anotou o erro; o servidor anota e segue para o próximo
                self._anotar(t, 'retomar falhou', f'{type(erro).__name__}: {erro}')

    def situacao(self, thread_id):
        """Para o financeiro e para os testes: status, decisões, se espera e se está parado."""
        valores = self.grafo.get_state(config(thread_id)).values
        return {'status': valores.get('status', ''), 'decisoes': valores.get('decisoes', []),
                'esperando': self.esperando(thread_id), 'parado': self.parado(thread_id)}
