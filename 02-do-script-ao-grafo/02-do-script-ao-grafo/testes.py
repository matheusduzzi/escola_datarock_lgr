"""O que os testes usam: carregar um grafo de um arquivo, rodar uma mensagem e rodar uma lista de testes.

Cada teste é uma função que recebe o módulo do grafo (o arquivo .py que tem montar_grafo).
"""
import importlib.util
import sys
from pathlib import Path

from atendimento_antigo import SistemaForaDoAr, sistema_consultar
from modelo_falso import ModeloFalso

RESPOSTA = '(resposta do modelo falso)'


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


class Sistema:
    """Conta as consultas. Com fora_do_ar=True, toda consulta falha."""

    def __init__(self, fora_do_ar=False):
        self.fora_do_ar = fora_do_ar
        self.chamadas = 0

    def __call__(self, numero):
        self.chamadas += 1
        if self.fora_do_ar:
            raise SistemaForaDoAr(f'consulta {self.chamadas} sem resposta')
        return sistema_consultar(numero)


def rodar(modulo, mensagem, fora_do_ar=False, grafo=None, modelo=None):
    """Roda uma mensagem. Retorna o estado final, o modelo falso e o sistema usados."""
    modelo = modelo or ModeloFalso([RESPOSTA])
    sistema = Sistema(fora_do_ar)
    grafo = grafo or modulo.montar_grafo(modelo, sistema)
    final = grafo.invoke({'mensagem': mensagem})
    return final, modelo, sistema


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
