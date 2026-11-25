"""Regras de texto do atendimento da Loja Exemplo.

Só usa a biblioteca padrão. Rode sozinho para ver para onde vai cada mensagem:

    python3 regras.py
"""
import csv
import re
import unicodedata
from collections import Counter
from pathlib import Path

PASTA = Path(__file__).resolve().parent
PEDIDOS_CSV = PASTA.parent / 'dados' / 'loja' / 'pedidos.csv'
MENSAGENS_CSV = PASTA.parent / 'dados' / 'loja' / 'mensagens.csv'

PALAVRAS_CANCELAMENTO = ('cancelar', 'cancelamento', 'desistir', 'desisti')
PALAVRAS_REEMBOLSO = ('reembolso', 'reembolsar', 'estorno', 'dinheiro de volta')
PALAVRAS_TROCA = ('troca', 'trocar', 'devolver', 'devolucao', 'defeito')
PALAVRAS_PEDIDO = ('pedido', 'entrega', 'rastreio', 'chegou')
ROTAS = ('pedido', 'troca', 'reembolso', 'humano', 'cancelamento')


def normalizar(texto):
    """Minúsculas e sem acento: "DEVOLUÇÃO" vira "devolucao"."""
    sem_acento = unicodedata.normalize('NFKD', texto or '')
    return ''.join(c for c in sem_acento if not unicodedata.combining(c)).lower()


def classificar_texto(texto):
    """Cancelamento ganha de reembolso, reembolso de troca, troca de pedido; sem nenhuma, humano."""
    t = normalizar(texto)
    if any(p in t for p in PALAVRAS_CANCELAMENTO):
        return 'cancelamento'
    if any(p in t for p in PALAVRAS_REEMBOLSO):
        return 'reembolso'
    if any(p in t for p in PALAVRAS_TROCA):
        return 'troca'
    if any(p in t for p in PALAVRAS_PEDIDO):
        return 'pedido'
    return 'humano'


def numero_do_pedido(texto):
    """O primeiro número da mensagem, ou None se não tem número."""
    achou = re.search(r'\d+', texto or '')
    return int(achou.group()) if achou else None


def ler_mensagens():
    with open(MENSAGENS_CSV, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


if __name__ == '__main__':
    mensagens = ler_mensagens()
    rotas = Counter(classificar_texto(m['texto']) for m in mensagens)
    erradas = [m['id_mensagem'] for m in mensagens if classificar_texto(m['texto']) != m['rota_esperada']]
    print(f'{len(mensagens)} mensagens: ' + ', '.join(f'{r} {rotas[r]}' for r in ROTAS))
    print(f'diferentes da rota esperada: {len(erradas)}')
    for texto in ('Quero o reembolso do pedido 52', 'Quero meu dinheiro de volta', 'Quero cancelar o pedido 27'):
        print(f'{texto!r:34} rota {classificar_texto(texto)}, número {numero_do_pedido(texto)}')
