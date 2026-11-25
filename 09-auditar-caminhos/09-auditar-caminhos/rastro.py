"""Mostra uma trilha exportada do servidor, reembolso por reembolso.

    python3 rastro.py exportado/trilha-de-terca.jsonl         todos os reembolsos
    python3 rastro.py exportado/trilha-de-terca.jsonl 101     só o pedido 101

Cada linha é uma passagem: a hora, onde aconteceu (um nó do grafo ou o servidor), o que
aconteceu e o detalhe. No fim de cada reembolso, o último passo: é onde ele está agora.
"""
import sys
from datetime import datetime

from testes import ler_trilha

FINAIS = {('reembolsar', 'terminou'), ('rejeitar', 'terminou')}


def hora(texto):
    return datetime.fromisoformat(texto).strftime('%d/%m %H:%M:%S')


def mostrar(trilha, pedido=None):
    threads = []
    for e in trilha:
        if e['thread'] not in threads and (pedido is None or e['pedido'] == pedido):
            threads.append(e['thread'])
    for t in threads:
        eventos = [e for e in trilha if e['thread'] == t]
        print(f"pedido {eventos[0]['pedido']} (thread {t[:6]})")
        for e in eventos:
            print(f"  {hora(e['quando'])}  {e['onde']:<10}  {e['evento']:<16}  {e['detalhe']}".rstrip())
        nos = [e for e in eventos if e['onde'] != 'servidor']
        ultimo = nos[-1] if nos else eventos[-1]
        terminou = any((e['onde'], e['evento']) in FINAIS for e in eventos)
        situacao = 'terminou' if terminou else f"parou em {ultimo['onde']} ({ultimo['evento']})"
        print(f'  último passo: {situacao}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('uso: python3 rastro.py <trilha.jsonl> [pedido]')
    mostrar(ler_trilha(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else None)
