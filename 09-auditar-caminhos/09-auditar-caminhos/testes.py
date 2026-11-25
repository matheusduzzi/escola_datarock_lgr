"""O que os scripts e os testes usam: carregar um servidor, ler e comparar trilhas, rodar testes.

Cada teste é uma função que recebe o módulo do servidor (o arquivo .py que tem Banco e
Atendimento). Um teste monta o próprio banco e a própria operadora: nada passa de um teste para
outro. Reiniciar o servidor é criar outro Atendimento com o mesmo banco e a mesma operadora.

As trilhas exportadas do servidor ficam em exportado/: uma linha JSON por passagem. O extrato
da operadora fica ao lado, num CSV. Para comparar uma trilha reproduzida com a exportada, a hora
e o código do thread saem da conta: a reprodução roda em outra hora e sorteia outros threads.
"""
import csv
import importlib.util
import json
import sys
from pathlib import Path

from externos import ForaDoAr, Operadora, Recusado  # noqa: F401

AQUI = Path(__file__).resolve().parent
TERCA = AQUI / 'exportado' / 'trilha-de-terca.jsonl'
EXTRATO_TERCA = AQUI / 'exportado' / 'estornos-de-terca.csv'
QUINTA = AQUI / 'exportado' / 'trilha-de-quinta.jsonl'
EXTRATO_QUINTA = AQUI / 'exportado' / 'estornos-de-quinta.csv'

ANA, BRUNO, DANIELA = 'financeiro.ana', 'financeiro.bruno', 'financeiro.daniela'
SEM_COBRANCA = 'Cliente 0112'  # pedido 4, Fone sem fio, 189,90, ainda aguardando pagamento
LUMINARIA = 'Cliente 0143'  # pedido 101, Luminária de mesa, 99,90: sai sem aprovação
DELA = 'Cliente 0198'  # pedido 29, Tênis de corrida, 349,90: vai para o financeiro
DELE = 'Cliente 0225'  # pedido 44, Cafeteira elétrica, 259,00: vai para o financeiro
NOVE_HORAS = '2026-11-25T09:00:00-03:00'


def relogio(hora):
    """Um relógio parado: a hora sai igual em toda chamada."""
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


def passagens(trilha, onde=None, evento=None):
    """As passagens da trilha que batem com o nó e o evento pedidos."""
    return [e for e in trilha if (onde is None or e['onde'] == onde) and (evento is None or e['evento'] == evento)]


def trilha_toda(at):
    """A trilha de todos os reembolsos do servidor, um thread depois do outro."""
    return [e for t in at.banco.donos for e in at.trilha_de(t)]


def ler_trilha(arquivo):
    with open(arquivo, encoding='utf-8') as f:
        return [json.loads(linha) for linha in f if linha.strip()]


def gravar_trilha(trilha, arquivo):
    with open(arquivo, 'w', encoding='utf-8') as f:
        for e in trilha:
            f.write(json.dumps(e, ensure_ascii=False) + '\n')


def ler_extrato(arquivo):
    """O extrato da operadora: um estorno por linha, com o pedido e o valor."""
    with open(arquivo, encoding='utf-8') as f:
        return [(int(l['id_pedido']), l['valor']) for l in csv.DictReader(f)]


def extrato(operadora):
    """O extrato de uma operadora do kit, no mesmo formato do ler_extrato."""
    return [(p['id_pedido'], f"{p['valor']:.2f}") for p in operadora.pagamentos]


def por_pedido(trilha):
    """A trilha separada por reembolso, sem hora e sem thread: {pedido: [(onde, evento, detalhe)]}.

    Se o mesmo pedido tem dois threads, o segundo vira 'pedido 44 (2)'.
    """
    nomes, grupos = {}, {}
    for e in trilha:
        if e['thread'] not in nomes:
            iguais = sum(1 for n in nomes.values() if str(n).split(' ')[0] == str(e['pedido']))
            nomes[e['thread']] = e['pedido'] if not iguais else f"{e['pedido']} ({iguais + 1})"
        grupos.setdefault(nomes[e['thread']], []).append((e['onde'], e['evento'], e['detalhe']))
    return grupos


def comparar(reproduzida, exportada):
    """Compara duas trilhas reembolso por reembolso. Retorna as diferenças; vazia quando batem."""
    a, b = por_pedido(reproduzida), por_pedido(exportada)
    diferencas = []
    for pedido in sorted(set(a) | set(b), key=lambda p: (len(str(p)), str(p))):
        x, y = a.get(pedido, []), b.get(pedido, [])
        if x == y:
            continue
        i = next((i for i, (p, q) in enumerate(zip(x, y)) if p != q), min(len(x), len(y)))
        aqui = ' '.join(x[i][:2]) if i < len(x) else 'fim'
        la = ' '.join(y[i][:2]) if i < len(y) else 'fim'
        diferencas.append(f'pedido {pedido}: passagem {i + 1} é "{aqui}" na reprodução e "{la}" na exportada')
    return diferencas


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
