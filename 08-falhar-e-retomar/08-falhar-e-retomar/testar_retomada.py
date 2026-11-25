"""Os testes da queda e da retomada do estorno.

    python3 testar_retomada.py                              testa servidor.py
    python3 testar_retomada.py versao_do_colega.py          testa outro arquivo
    python3 testar_retomada.py servidor.py nome_do_teste    roda só esse teste

A queda depois do estorno e a queda antes andam juntas: depois de retomar, o dinheiro do pedido
saiu uma vez, nem zero nem duas. E o banco diz em que pé ficou cada estorno.
"""
import sys

from testes import ANA, BRUNO, DELA, DELE, LUMINARIA, NOVE_HORAS, Operadora, pagos, relogio, rodar_testes


def teste_sem_queda_paga_uma_vez(m):
    op = Operadora()
    at = m.Atendimento(m.Banco(), op)
    t, _ = at.pedir_reembolso(LUMINARIA, 101)
    assert at.situacao(t)['status'] == 'reembolsado', at.situacao(t)
    assert pagos(op, 101) == 1, op.pagamentos


def teste_queda_depois_de_pagar_nao_paga_de_novo(m):
    op = Operadora()
    at = m.Atendimento(m.Banco(), op)
    op.cair('depois')
    t, _ = at.pedir_reembolso(LUMINARIA, 101)
    at.retomar(t)
    assert at.situacao(t)['status'] == 'reembolsado', at.situacao(t)
    assert pagos(op, 101) == 1, op.pagamentos


def teste_queda_antes_de_pagar_paga_na_retomada(m):
    op = Operadora()
    at = m.Atendimento(m.Banco(), op)
    op.cair('antes')
    t, _ = at.pedir_reembolso(LUMINARIA, 101)
    assert pagos(op, 101) == 0, op.pagamentos
    at.retomar(t)
    assert at.situacao(t)['status'] == 'reembolsado', at.situacao(t)
    assert pagos(op, 101) == 1, op.pagamentos


def teste_queda_deixa_parado_sem_status(m):
    op = Operadora()
    at = m.Atendimento(m.Banco(), op)
    op.cair('depois')
    t, resposta = at.pedir_reembolso(LUMINARIA, 101)
    s = at.situacao(t)
    assert (s['status'], s['parado'], s['esperando']) == ('', True, False), (s, resposta)
    assert at.parados() == [t], at.parados()


def teste_retoma_depois_do_reinicio_sem_nova_decisao(m):
    banco, op = m.Banco(), Operadora()
    manha = m.Atendimento(banco, op, relogio(NOVE_HORAS))
    t, _ = manha.pedir_reembolso(DELA, 29)
    op.cair('depois')
    manha.decidir(t, ANA, True)
    tarde = m.Atendimento(banco, op)  # o servidor reinicia; o banco e a operadora continuam
    for parado in tarde.parados():
        tarde.retomar(parado)
    s = tarde.situacao(t)
    assert (s['status'], len(s['decisoes'])) == ('reembolsado', 1), s
    assert s['decisoes'][0]['quem'] == ANA, s
    assert pagos(op, 29) == 1, op.pagamentos


def teste_registro_do_efeito_depois_da_retomada(m):
    banco, op = m.Banco(), Operadora()
    at = m.Atendimento(banco, op)
    op.cair('depois')
    t, _ = at.pedir_reembolso(LUMINARIA, 101)
    at.retomar(t)
    efeito = banco.efeitos['estorno-101']
    assert (efeito['status'], efeito['tentativas']) == ('feito', 2), efeito
    assert efeito['id_pagamento'] == op.pagamentos[0]['id_pagamento'], (efeito, op.pagamentos)


def teste_registro_mostra_o_estorno_no_meio(m):
    banco, op = m.Banco(), Operadora()
    at = m.Atendimento(banco, op)
    op.cair('antes')
    at.pedir_reembolso(LUMINARIA, 101)
    efeito = banco.efeitos['estorno-101']
    assert (efeito['status'], efeito['id_pagamento']) == ('enviado', ''), efeito


def teste_mesmo_pedido_duas_vezes_paga_uma(m):
    op = Operadora()
    at = m.Atendimento(m.Banco(), op, relogio(NOVE_HORAS))
    primeiro, _ = at.pedir_reembolso(DELE, 44)
    segundo, _ = at.pedir_reembolso(DELE, 44)  # a cliente clicou duas vezes
    at.decidir(primeiro, ANA, True)
    at.decidir(segundo, BRUNO, True)
    assert [at.situacao(t)['status'] for t in (primeiro, segundo)] == ['reembolsado', 'reembolsado']
    assert pagos(op, 44) == 1, op.pagamentos


def teste_retomar_o_que_terminou_nao_paga(m):
    op = Operadora()
    at = m.Atendimento(m.Banco(), op)
    t, _ = at.pedir_reembolso(LUMINARIA, 101)
    resposta = at.retomar(t)
    assert resposta == m.NADA_PARA_RETOMAR, resposta
    assert pagos(op, 101) == 1, op.pagamentos


def teste_pausa_da_aula_07_continua(m):
    op = Operadora()
    at = m.Atendimento(m.Banco(), op, relogio(NOVE_HORAS))
    t, _ = at.pedir_reembolso(DELA, 29)
    assert at.situacao(t)['esperando'] and pagos(op, 29) == 0, op.pagamentos
    at.decidir(t, ANA, False)
    assert at.situacao(t)['status'] == 'rejeitado' and pagos(op, 29) == 0, op.pagamentos
    assert at.decidir(t, BRUNO, True) == m.NADA_ESPERANDO and pagos(op, 29) == 0, op.pagamentos


TESTES = [teste_sem_queda_paga_uma_vez, teste_queda_depois_de_pagar_nao_paga_de_novo,
          teste_queda_antes_de_pagar_paga_na_retomada, teste_queda_deixa_parado_sem_status,
          teste_retoma_depois_do_reinicio_sem_nova_decisao, teste_registro_do_efeito_depois_da_retomada,
          teste_registro_mostra_o_estorno_no_meio, teste_mesmo_pedido_duas_vezes_paga_uma,
          teste_retomar_o_que_terminou_nao_paga, teste_pausa_da_aula_07_continua]

if __name__ == '__main__':
    sys.exit(rodar_testes(TESTES, sys.argv[1] if len(sys.argv) > 1 else 'servidor.py', sys.argv[2:]))
