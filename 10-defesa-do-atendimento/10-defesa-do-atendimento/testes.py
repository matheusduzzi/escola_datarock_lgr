"""Ferramentas dos testes da aula: carregar um grafo, abrir uma conversa e rodar uma lista de testes.

Cada conversa tem o próprio grafo, o próprio sistema de pedidos, o próprio sistema de
pagamentos e um thread_id só dela. Cada teste é uma função que recebe o módulo do grafo.
"""
import importlib.util
import itertools
import sys
from pathlib import Path

from langgraph.types import Command

from pagamentos import Pagamentos
from sistema import SistemaPedidos

LIMITE = 10  # passos por chamada nos testes; a chamada mais longa da defesa roda 6 passos
_numero = itertools.count(1)


def carregar(caminho):
    caminho = Path(caminho).resolve()
    if not caminho.is_file():
        sys.exit(f'arquivo não encontrado: {caminho.name}')
    nome = f'{caminho.stem}_{len(sys.modules)}'  # nome único: dá para carregar duas cópias
    spec = importlib.util.spec_from_file_location(nome, caminho)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nome] = modulo  # o StateGraph lê as anotações do Estado pelo módulo
    spec.loader.exec_module(modulo)
    return modulo


class Conversa:
    """Uma conversa de um cliente com o atendimento.

        c = Conversa(modulo, 'Cliente 0198', falha_pagamento='depois')
        c.enviar('Quero o reembolso do pedido 29')   # pausa para o financeiro
        c.financeiro(True)                           # a pessoa responde; aqui o pagamento cai
        c.continuar()                                # invoke(None): continua de onde parou
    """

    def __init__(self, modulo, cliente, falhas=0, falha_pagamento=None):
        self.sistema = SistemaPedidos(falhas=falhas)
        self.pagamentos = Pagamentos(falha=falha_pagamento)
        self.grafo = modulo.montar_grafo(self.sistema, self.pagamentos)
        self.config = {'configurable': {'thread_id': f'conversa-{next(_numero)}'}, 'recursion_limit': LIMITE}
        self.cliente = cliente

    def enviar(self, mensagem):
        return self.grafo.invoke({'mensagem': mensagem, 'cliente': self.cliente}, self.config)

    def financeiro(self, resposta):
        return self.grafo.invoke(Command(resume=resposta), self.config)

    def continuar(self):
        return self.grafo.invoke(None, self.config)

    def proximo(self):
        """Os nós que o checkpoint diz que rodam a seguir. Vazio quando a conversa terminou."""
        return self.grafo.get_state(self.config).next


def pausou(resultado):
    return '__interrupt__' in resultado


def rodar_testes(testes, caminho):
    modulo = carregar(caminho)
    passaram = 0
    for teste in testes:
        try:
            teste(modulo)
        except Exception as erro:  # o teste falhou ou o grafo levantou erro
            linha = (str(erro).splitlines() or [''])[0]
            print(f'FALHOU {teste.__name__}: {type(erro).__name__}: {linha}'.rstrip())
        else:
            passaram += 1
            print(f'ok     {teste.__name__}')
    print(f'{passaram} de {len(testes)} testes passaram com {Path(caminho).name}')
    return 0 if passaram == len(testes) else 1
