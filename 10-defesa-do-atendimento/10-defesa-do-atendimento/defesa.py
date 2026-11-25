"""As três execuções da defesa, passo a passo.

    python3 defesa.py normal
    python3 defesa.py negacao
    python3 defesa.py retomada
    python3 defesa.py retomada versao_do_colega.py

Opções para mudar o caso:
    --resposta "não"   o que o financeiro responde (True, False ou um texto)
    --falha antes      quando o pagamento cai: antes ou depois de gravar
"""
import argparse

from pagamentos import PagamentosFora
from testes import Conversa, carregar, pausou

CASOS = {
    'normal': ('Cliente 0098', 'Quero o reembolso do pedido 52', None, None),
    'negacao': ('Cliente 0143', 'Quero o reembolso do pedido 7', False, None),
    'retomada': ('Cliente 0198', 'Quero o reembolso do pedido 29', True, 'depois'),
}


def ler_resposta(texto):
    """True e False viram o valor do Python; qualquer outro texto fica como texto."""
    return {'True': True, 'False': False}.get(texto, texto)


def main():
    p = argparse.ArgumentParser(description='As três execuções da defesa.')
    p.add_argument('caso', choices=CASOS)
    p.add_argument('arquivo', nargs='?', default='atendimento.py')
    p.add_argument('--resposta', type=ler_resposta)
    p.add_argument('--falha', choices=['antes', 'depois'])
    a = p.parse_args()
    cliente, mensagem, resposta, falha = CASOS[a.caso]
    if a.resposta is not None:
        resposta = a.resposta
    falha = a.falha or falha
    c = Conversa(carregar(a.arquivo), cliente, falha_pagamento=falha)
    print(f'{a.arquivo} | {cliente}: {mensagem}')
    resultado = c.enviar(mensagem)
    if pausou(resultado):
        print('pausou antes de:', ', '.join(c.proximo()))
        print('o financeiro vê:', resultado['__interrupt__'][0].value)
        print('o financeiro responde:', repr(resposta))
        try:
            resultado = c.financeiro(resposta)
        except PagamentosFora as erro:
            print(f'caiu: PagamentosFora: {erro}')
            print('o checkpoint diz que falta:', ', '.join(c.proximo()))
            resultado = c.continuar()
            print('continuou com invoke(None)')
    print('caminho:', ' > '.join(resultado['caminho']))
    print('resposta:', resultado['resposta'])
    if resultado.get('motivo'):
        print('motivo:', resultado['motivo'])
    print(f'pagamentos: {c.pagamentos.chamadas} chamada(s), {len(c.pagamentos.gravados)} reembolso(s) gravado(s)')


if __name__ == '__main__':
    main()
