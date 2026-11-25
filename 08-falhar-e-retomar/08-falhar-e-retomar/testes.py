"""O que os testes usam: carregar um servidor, um relógio parado, contar estornos e rodar testes.

Cada teste é uma função que recebe o módulo do servidor (o arquivo .py que tem Banco e
Atendimento). Um teste monta o próprio banco e a própria operadora: nada passa de um teste para
outro. Reiniciar o servidor é criar outro Atendimento com o mesmo banco e a mesma operadora: a
operadora é de fora da loja e não reinicia junto.
"""
import importlib.util
import sys
from pathlib import Path

from externos import ForaDoAr, Mensageiro, Operadora  # noqa: F401

ANA, BRUNO = 'financeiro.ana', 'financeiro.bruno'  # duas pessoas do financeiro
DELA = 'Cliente 0198'  # pedido 29, Tênis de corrida, 349,90
DELE = 'Cliente 0225'  # pedido 44, Cafeteira elétrica, 259,00
LUMINARIA = 'Cliente 0143'  # pedido 101, Luminária de mesa, 99,90: sai sem aprovação
NOVE_HORAS = '2026-11-25T09:00:00-03:00'
TARDE = '2026-11-25T15:40:00-03:00'


def relogio(hora):
    """Um relógio parado: a hora da decisão sai igual em toda rodada."""
    return lambda: hora


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


def pagos(operadora, id_pedido):
    """Quantas vezes o dinheiro desse pedido saiu na operadora."""
    return sum(1 for p in operadora.pagamentos if p['id_pedido'] == id_pedido)


def enviadas(mensageiro, cliente):
    """Quantas mensagens chegaram para essa cliente."""
    return sum(1 for m in mensageiro.mensagens if m['cliente'] == cliente)


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
