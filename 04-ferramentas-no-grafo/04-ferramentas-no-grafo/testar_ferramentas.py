"""Testes das ferramentas do atendimento: a decisão do modelo de um lado, o efeito do outro.

    python3 testar_ferramentas.py                       testa atendimento.py
    python3 testar_ferramentas.py versao_do_colega.py   testa outro arquivo
"""
import sys

from langchain_core.messages import HumanMessage

from sistema import SistemaPedidos
from testes import conversar, decidir_na_mao, rodar_testes, schema_do_modelo

CLIENTE = 'Cliente 0036'  # pedidos 40 (aguardando pagamento), 78 (em separação) e 109 (enviado)


def teste_decidir_nao_mexe_no_sistema(m):
    sistema = SistemaPedidos()
    modelo = m.ModeloFalsoLoja().bind_tools(m.criar_ferramentas(sistema))
    decisao = modelo.invoke([HumanMessage('Quero cancelar o pedido 109')])
    assert decisao.tool_calls[0]['name'] == 'cancelar_pedido', decisao.tool_calls
    assert decisao.tool_calls[0]['args'] == {'id_pedido': 109}, decisao.tool_calls
    assert sistema.efeitos == [], sistema.efeitos


def teste_consulta_nao_tem_efeito(m):
    resposta, sistema = conversar(m, CLIENTE, 'O pedido 40 já foi enviado?')
    assert 'aguardando pagamento' in resposta, resposta
    assert sistema.efeitos == [], sistema.efeitos


def teste_cancela_aguardando_pagamento(m):
    resposta, sistema = conversar(m, CLIENTE, 'Quero cancelar o pedido 40')
    assert sistema.efeitos == [('cancelar', 40)], sistema.efeitos


def teste_cancela_em_separacao(m):
    resposta, sistema = conversar(m, CLIENTE, 'Quero cancelar o pedido 78')
    assert sistema.efeitos == [('cancelar', 78)], sistema.efeitos


def teste_nao_cancela_pedido_que_saiu(m):
    resposta, sistema = conversar(m, CLIENTE, 'Quero cancelar o pedido 109')
    assert sistema.efeitos == [], sistema.efeitos
    assert 'enviado' in resposta, resposta


def teste_nao_cancela_pedido_de_outra_pessoa(m):
    resposta, sistema = conversar(m, CLIENTE, 'Quero cancelar o pedido 27')
    assert sistema.efeitos == [], sistema.efeitos
    assert 'não está no seu cadastro' in resposta, resposta


def teste_pedido_que_nao_existe(m):
    resposta, sistema = conversar(m, CLIENTE, 'Quero cancelar o pedido 999')
    assert sistema.efeitos == [], sistema.efeitos
    assert 'não está no seu cadastro' in resposta, resposta


def teste_formato_errado_nao_chega_ao_efeito(m):
    for args in ({'id_pedido': True}, {'id_pedido': 0}, {'id_pedido': 'quarenta'}, {}):
        msg, sistema = decidir_na_mao(m, CLIENTE, 'cancelar_pedido', args)
        assert msg.status == 'error', (args, msg.status, msg.content)
        assert sistema.efeitos == [], (args, sistema.efeitos)


def teste_cliente_vem_da_conversa(m):
    assert 'cliente' not in schema_do_modelo(m, 'cancelar_pedido'), 'o modelo vê o argumento cliente'
    msg, sistema = decidir_na_mao(m, CLIENTE, 'cancelar_pedido', {'id_pedido': 27, 'cliente': 'Cliente 0253'})
    assert sistema.efeitos == [], sistema.efeitos


TESTES = [teste_decidir_nao_mexe_no_sistema, teste_consulta_nao_tem_efeito, teste_cancela_aguardando_pagamento,
          teste_cancela_em_separacao, teste_nao_cancela_pedido_que_saiu, teste_nao_cancela_pedido_de_outra_pessoa,
          teste_pedido_que_nao_existe, teste_formato_errado_nao_chega_ao_efeito, teste_cliente_vem_da_conversa]

if __name__ == '__main__':
    sys.exit(rodar_testes(TESTES, sys.argv[1] if len(sys.argv) > 1 else 'atendimento.py'))
