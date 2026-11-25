"""O que os testes usam: carregar um grafo, conversar, mandar uma decisão escrita na mão e rodar testes.

Cada teste é uma função que recebe o módulo do atendimento (o arquivo .py que tem
criar_ferramentas, montar_grafo e Estado).
"""
import importlib.util
import sys
from pathlib import Path

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from sistema import SistemaPedidos

LIMITE = 10  # passos por conversa nos testes; uma conversa com uma ferramenta usa 3


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


def conversar(modulo, cliente, mensagem):
    """Uma mensagem do cliente pelo grafo inteiro, com o modelo falso. Retorna a resposta e o sistema."""
    sistema = SistemaPedidos()
    final = modulo.montar_grafo(sistema).invoke({'messages': [('user', mensagem)], 'cliente': cliente},
                                                {'recursion_limit': LIMITE})
    return final['messages'][-1].content, sistema


def decidir_na_mao(modulo, cliente, ferramenta, args):
    """Pula o modelo: entrega ao nó de ferramentas uma decisão escrita na mão.

    Retorna a ToolMessage (status 'success' ou 'error') e o sistema, para ver os efeitos.
    """
    sistema = SistemaPedidos()
    g = StateGraph(modulo.Estado)
    g.add_node('tools', ToolNode(modulo.criar_ferramentas(sistema)))
    g.add_edge(START, 'tools')
    g.add_edge('tools', END)
    decisao = AIMessage(content='', tool_calls=[{'name': ferramenta, 'args': args, 'id': 'na-mao'}])
    final = g.compile().invoke({'messages': [decisao], 'cliente': cliente})
    return final['messages'][-1], sistema


def schema_do_modelo(modulo, ferramenta):
    """Os argumentos que o modelo vê para essa ferramenta."""
    sistema = SistemaPedidos()
    for t in modulo.criar_ferramentas(sistema):
        if t.name == ferramenta:
            return t.tool_call_schema.model_json_schema()['properties']
    raise AssertionError(f'ferramenta {ferramenta} não existe')


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
