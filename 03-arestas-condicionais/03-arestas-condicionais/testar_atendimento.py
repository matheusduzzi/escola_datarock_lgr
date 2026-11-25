"""Testes de caminhos e de término do atendimento.

    python3 testar_atendimento.py                       testa atendimento.py
    python3 testar_atendimento.py versao_do_colega.py   testa outro arquivo com montar_grafo
"""
import sys
from collections import Counter

from regras import ler_mensagens
from testes import rodar, rodar_testes


def teste_pedido_que_existe(m):
    final, _ = rodar(m, 'O pedido 84 já foi enviado?')
    assert final['caminho'] == ['classificar', 'consultar', 'responder'], final['caminho']
    assert 'pedido 84' in final['resposta'], final['resposta']


def teste_pedido_sem_numero(m):
    final, sistema = rodar(m, 'Onde está a ENTREGA?')
    assert final['caminho'] == ['classificar', 'consultar', 'pedir_numero'], final['caminho']
    assert sistema.chamadas == 0, sistema.chamadas


def teste_pedido_que_nao_existe(m):
    final, _ = rodar(m, 'Cadê o meu pedido 999?')
    assert final['caminho'] == ['classificar', 'consultar', 'humano'], final['caminho']
    assert final['motivo'] == 'pedido 999 não existe', final['motivo']


def teste_sistema_volta_na_terceira(m):
    final, sistema = rodar(m, 'O pedido 84 já foi enviado?', falhas=2)
    assert final['caminho'] == ['classificar', 'consultar', 'consultar', 'consultar', 'responder'], final['caminho']
    assert sistema.chamadas == 3, sistema.chamadas


def teste_sistema_fora_do_ar(m):
    final, sistema = rodar(m, 'O pedido 84 já foi enviado?', falhas=None)
    assert final['caminho'] == ['classificar', 'consultar', 'consultar', 'consultar', 'humano'], final['caminho']
    assert sistema.chamadas == 3, sistema.chamadas
    assert 'sem resposta em 3 tentativas' in final['motivo'], final['motivo']


def teste_troca(m):
    final, _ = rodar(m, 'Quero trocar o produto do pedido 59')
    assert final['caminho'] == ['classificar', 'troca'], final['caminho']


def teste_sem_assunto_e_vazia(m):
    for texto in ('Bom dia', '', '   '):
        final, _ = rodar(m, texto)
        assert final['caminho'] == ['classificar', 'humano'], (texto, final['caminho'])


def teste_rota_sem_destino(m):
    final, sistema = rodar(m, 'Quero cancelar o pedido 27')
    assert final['caminho'] == ['classificar', 'humano'], final['caminho']
    assert final['motivo'] == 'rota sem destino: cancelamento', final['motivo']
    assert sistema.chamadas == 0, sistema.chamadas


def teste_59_mensagens_terminam(m):
    primeiro = {'pedido': 'consultar', 'troca': 'troca', 'humano': 'humano'}
    fim = Counter()
    for msg in ler_mensagens():
        final, _ = rodar(m, msg['texto'])
        assert final['caminho'][1] == primeiro[msg['rota_esperada']], (msg['id_mensagem'], final['caminho'])
        assert final['caminho'][-1] == final['atendido_por'], (msg['id_mensagem'], final['caminho'])
        fim[final['atendido_por']] += 1
    assert fim == {'responder': 18, 'pedir_numero': 1, 'troca': 20, 'humano': 20}, dict(fim)


TESTES = [teste_pedido_que_existe, teste_pedido_sem_numero, teste_pedido_que_nao_existe,
          teste_sistema_volta_na_terceira, teste_sistema_fora_do_ar, teste_troca, teste_sem_assunto_e_vazia,
          teste_rota_sem_destino, teste_59_mensagens_terminam]

if __name__ == '__main__':
    sys.exit(rodar_testes(TESTES, sys.argv[1] if len(sys.argv) > 1 else 'atendimento.py'))
