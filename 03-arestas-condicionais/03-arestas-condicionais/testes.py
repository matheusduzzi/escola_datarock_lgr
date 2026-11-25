"""Ferramentas dos testes da aula: carregar um grafo, rodar uma mensagem, rodar uma lista de testes.

Cada teste é uma função que recebe o módulo do grafo (o arquivo .py que tem montar_grafo).
"""
import importlib.util
import sys
from pathlib import Path

from sistema import SistemaPedidos

LIMITE = 10  # passos por mensagem nos testes; o caminho mais longo do atendimento tem 5


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


def rodar(modulo, mensagem, falhas=0):
    """Roda uma mensagem com o limite de passos. Retorna o estado final e o sistema usado.

    Se o grafo passar de LIMITE passos, o LangGraph levanta GraphRecursionError e o teste falha.
    """
    sistema = SistemaPedidos(falhas=falhas)
    final = modulo.montar_grafo(sistema).invoke({'mensagem': mensagem}, {'recursion_limit': LIMITE})
    return final, sistema


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
