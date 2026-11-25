"""Os testes da defesa: execução normal, negação, retomada depois de falha e término.

    python3 testar_defesa.py                        testa o atendimento.py
    python3 testar_defesa.py versao_do_colega.py    testa outro arquivo com montar_grafo
"""
import sys
from collections import Counter

from pagamentos import PagamentosFora
from regras import ler_mensagens
from testes import Conversa, pausou, rodar_testes


def teste_execucao_normal(m):
    """Pedido 52, R$ 79,90, entregue: reembolsa sem pausar, uma vez."""
    c = Conversa(m, 'Cliente 0098')
    final = c.enviar('Quero o reembolso do pedido 52')
    assert not pausou(final), 'pausou num reembolso abaixo do limite'
    assert final['caminho'] == ['classificar', 'consultar', 'validar', 'reembolsar'], final['caminho']
    assert len(c.pagamentos.gravados) == 1, c.pagamentos.gravados
    assert c.proximo() == (), c.proximo()


def teste_negacao(m):
    """Pedido 7, R$ 850,00: pausa, o financeiro nega, nada sai."""
    c = Conversa(m, 'Cliente 0143')
    primeira = c.enviar('Quero o reembolso do pedido 7')
    assert pausou(primeira), 'não pausou num reembolso acima do limite'
    assert c.proximo() == ('aprovar',), c.proximo()
    assert c.pagamentos.chamadas == 0, 'chamou o pagamento antes da decisão'
    final = c.financeiro(False)
    assert final['caminho'] == ['classificar', 'consultar', 'validar', 'aprovar', 'negar'], final['caminho']
    assert c.pagamentos.chamadas == 0 and not c.pagamentos.gravados, c.pagamentos.gravados


def teste_retomada_depois_de_falha(m):
    """Pedido 29, R$ 349,90: aprovado, o pagamento grava e a confirmação se perde; continuar não repete."""
    c = Conversa(m, 'Cliente 0198', falha_pagamento='depois')
    assert pausou(c.enviar('Quero o reembolso do pedido 29'))
    try:
        c.financeiro(True)
    except PagamentosFora:
        pass
    else:
        raise AssertionError('o pagamento não caiu: o teste não chegou à falha')
    assert c.proximo() == ('reembolsar',), c.proximo()
    final = c.continuar()
    assert final['atendido_por'] == 'reembolsar', final.get('atendido_por')
    assert c.pagamentos.chamadas == 2, c.pagamentos.chamadas
    assert len(c.pagamentos.gravados) == 1, f'{len(c.pagamentos.gravados)} reembolsos gravados'


def teste_59_mensagens_terminam(m):
    """Nenhuma das 59 mensagens é reembolso; todas terminam num nó que responde, sem pausa."""
    fim = Counter()
    for msg in ler_mensagens():
        final = Conversa(m, 'Cliente 0001').enviar(msg['texto'])
        assert not pausou(final), msg['id_mensagem']
        fim[final['atendido_por']] += 1
    assert fim == Counter({'responder': 18, 'pedir_numero': 1, 'troca': 20, 'humano': 20}), dict(fim)


TESTES = [teste_execucao_normal, teste_negacao, teste_retomada_depois_de_falha, teste_59_mensagens_terminam]

if __name__ == '__main__':
    sys.exit(rodar_testes(TESTES, sys.argv[1] if len(sys.argv) > 1 else 'atendimento.py'))
