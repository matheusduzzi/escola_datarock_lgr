"""O atendimento da Loja Exemplo do jeito que ele era: um script, um if atrás do outro.

Só usa a biblioteca padrão. Rode de dentro dessa pasta:

    python3 atendimento_antigo.py                 # as 59 mensagens do kit
    python3 atendimento_antigo.py "Bom dia"       # uma mensagem

Na aula você desenha o que esse script faz com cada mensagem. Não corrija o script: ele fica
assim para o desenho mostrar onde ele falha.
"""
import csv
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

PASTA = Path(__file__).resolve().parent
PEDIDOS_CSV = PASTA.parent / 'dados' / 'loja' / 'pedidos.csv'
MENSAGENS_CSV = PASTA.parent / 'dados' / 'loja' / 'mensagens.csv'

PALAVRAS_REEMBOLSO = ('reembolso', 'dinheiro de volta', 'estorno')
PALAVRAS_TROCA = ('troca', 'trocar', 'devolver', 'devolucao', 'defeito')
PALAVRAS_PEDIDO = ('pedido', 'entrega', 'rastreio', 'chegou')


class SistemaForaDoAr(Exception):
    """O sistema de pedidos não respondeu."""


def normalizar(texto):
    """Minúsculas e sem acento: "DEVOLUÇÃO" vira "devolucao"."""
    sem_acento = unicodedata.normalize('NFKD', texto or '')
    return ''.join(c for c in sem_acento if not unicodedata.combining(c)).lower()


def tem(texto, palavras):
    return any(p in texto for p in palavras)


def numero_do_pedido(texto):
    """O primeiro número da mensagem, ou None se não tem número."""
    achou = re.search(r'\d+', texto or '')
    return int(achou.group()) if achou else None


def sistema_consultar(numero):
    """Consulta o sistema de pedidos. No kit ele nunca cai; na loja, às vezes caía."""
    with open(PEDIDOS_CSV, encoding='utf-8', newline='') as f:
        for linha in csv.DictReader(f):
            if int(linha['id_pedido']) == numero:
                return linha
    return None


def consultar_ate_responder(numero):
    while True:  # tenta de novo até o sistema responder
        try:
            return sistema_consultar(numero)
        except SistemaForaDoAr:
            continue


def reembolsar(pedido):
    # Aqui o script chamava o serviço de pagamentos. No kit, só monta o texto.
    return f"Pronto, devolvi {pedido['valor']} reais do pedido {pedido['id_pedido']}."


def atender(texto):
    t = normalizar(texto)
    if tem(t, PALAVRAS_REEMBOLSO):
        numero = numero_do_pedido(texto)
        if numero is None:
            return 'Qual é o número do pedido?'
        pedido = consultar_ate_responder(numero)
        if pedido is None:
            return f'Não achei o pedido {numero}.'
        return reembolsar(pedido)
    if tem(t, PALAVRAS_TROCA):
        return 'Para trocar, abra a página de trocas da loja e informe o número do pedido.'
    if tem(t, PALAVRAS_PEDIDO):
        numero = numero_do_pedido(texto)
        if numero is None:
            return 'Qual é o número do pedido?'
        pedido = consultar_ate_responder(numero)
        if pedido is None:
            return f'Não achei o pedido {numero}.'
        return f"O pedido {numero} está {pedido['status']}."
    if 'pessoa' in t:
        return 'Vou passar para uma pessoa da equipe.'


def ler_mensagens():
    with open(MENSAGENS_CSV, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        print('resposta:', atender(sys.argv[1]))
    else:
        mensagens = ler_mensagens()
        sem = Counter(m['texto'] for m in mensagens if atender(m['texto']) is None)
        total = sum(sem.values())
        print(f'{len(mensagens)} mensagens: {len(mensagens) - total} com resposta, {total} sem resposta')
        for texto, vezes in sem.most_common():
            print(f'  sem resposta: {texto!r} {vezes}x')
