"""O que os testes usam: carregar um servidor, olhar o banco e rodar uma lista de testes.

Cada teste é uma função que recebe o módulo do servidor (o arquivo .py que tem Banco,
Atendimento e config). Um teste monta o próprio banco: nada passa de um teste para outro.
"""
import importlib.util
import sys
from pathlib import Path

DELA = 'Cliente 0143'  # pedidos 7 (entregue, 850,00) e 101 (enviado, 99,90)
DELE = 'Cliente 0050'  # pedido 10 (aguardando pagamento, 129,00)
RECUSA = 'Não achei essa conversa na sua conta.'


def carregar(caminho):
    caminho = Path(caminho).resolve()
    if not caminho.is_file():
        sys.exit(f'arquivo não encontrado: {caminho.name}')
    nome = f'{caminho.stem}_{len(sys.modules)}'  # nome único: dá para carregar duas cópias
    spec = importlib.util.spec_from_file_location(nome, caminho)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nome] = modulo
    spec.loader.exec_module(modulo)
    return modulo


def config(thread_id):
    return {'configurable': {'thread_id': thread_id}}


def contar_fotos(atendimento, thread_id):
    """Quantos checkpoints o banco tem dessa conversa."""
    return len(list(atendimento.grafo.get_state_history(config(thread_id))))


def textos(atendimento, thread_id):
    """As mensagens salvas dessa conversa, só o texto, da mais velha para a mais nova."""
    estado = atendimento.grafo.get_state(config(thread_id))
    return [m.content for m in estado.values.get('messages', [])]


def rodar_testes(testes, caminho, nomes=()):
    modulo = carregar(caminho)
    if nomes:
        testes = [t for t in testes if t.__name__ in nomes]
    passaram = 0
    for teste in testes:
        try:
            teste(modulo)
        except Exception as erro:  # o teste falhou ou o servidor levantou erro
            linha = (str(erro).splitlines() or [''])[0]
            print(f'FALHOU {teste.__name__}: {type(erro).__name__}: {linha}'.rstrip())
        else:
            passaram += 1
            print(f'ok     {teste.__name__}')
    print(f'{passaram} de {len(testes)} testes passaram com {Path(caminho).name}')
    return 0 if passaram == len(testes) else 1
