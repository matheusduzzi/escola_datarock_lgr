"""Os testes da trilha e da investigação de um reembolso parado.

    python3 testar_trilha.py                              testa servidor.py
    python3 testar_trilha.py versao_do_colega.py          testa outro arquivo
    python3 testar_trilha.py servidor.py nome_do_teste    roda só esse teste

Os testes leem a trilha pelo `trilha_de` de cada reembolso. A trilha precisa contar o que
terminou e também o que pausou, caiu ou foi recusado, com quem e quando.
"""
import sys

from testes import (ANA, DANIELA, DELA, DELE, EXTRATO_TERCA, LUMINARIA, NOVE_HORAS, SEM_COBRANCA, TERCA,
                    Operadora, Recusado, comparar, extrato, ler_extrato, ler_trilha, pagos, passagens, relogio,
                    rodar_testes, trilha_toda)


def curta(trilha):
    """A trilha numa linha, para a mensagem do teste que falha."""
    return ' > '.join(f"{e['onde']} {e['evento']}" for e in trilha) or 'vazia'


def nos_que_terminaram(trilha):
    return [e['onde'] for e in passagens(trilha, evento='terminou')]


def pedir_sem_cobranca(at):
    """O pedido 4 ainda espera pagamento: a operadora recusa, e o erro sobe até a tela da cliente."""
    try:
        at.pedir_reembolso(SEM_COBRANCA, 4)
    except Recusado:
        return next(t for t, c in at.banco.donos.items() if c == SEM_COBRANCA)
    raise AssertionError('o pedido 4 devia ter sido recusado pela operadora')


def teste_reembolso_direto_passa_pelos_nos_na_ordem(m):
    at = m.Atendimento(m.Banco(), Operadora())
    t, _ = at.pedir_reembolso(LUMINARIA, 101)
    assert nos_que_terminaram(at.trilha_de(t)) == ['preparar', 'reembolsar'], curta(at.trilha_de(t))


def teste_rejeicao_passa_pelo_rejeitar(m):
    at = m.Atendimento(m.Banco(), Operadora(), relogio(NOVE_HORAS))
    t, _ = at.pedir_reembolso(DELA, 29)
    at.decidir(t, ANA, False)
    assert nos_que_terminaram(at.trilha_de(t)) == ['preparar', 'aprovar', 'rejeitar'], curta(at.trilha_de(t))


def teste_cada_thread_tem_a_sua_trilha(m):
    at = m.Atendimento(m.Banco(), Operadora())
    luminaria, _ = at.pedir_reembolso(LUMINARIA, 101)
    cafeteira, _ = at.pedir_reembolso(DELE, 44)
    assert {e['pedido'] for e in at.trilha_de(luminaria)} == {101}, curta(at.trilha_de(luminaria))
    assert nos_que_terminaram(at.trilha_de(cafeteira)) == ['preparar'], curta(at.trilha_de(cafeteira))


def teste_trilha_continua_depois_do_reinicio(m):
    banco, op = m.Banco(), Operadora()
    manha = m.Atendimento(banco, op, relogio(NOVE_HORAS))
    t, _ = manha.pedir_reembolso(DELA, 29)
    antes = manha.trilha_de(t)
    tarde = m.Atendimento(banco, op, relogio(NOVE_HORAS))  # o servidor reinicia; o banco continua
    assert tarde.trilha_de(t) == antes, curta(tarde.trilha_de(t))
    tarde.decidir(t, ANA, True)
    assert nos_que_terminaram(tarde.trilha_de(t)) == ['preparar', 'aprovar', 'reembolsar'], curta(tarde.trilha_de(t))


def teste_retomada_da_aula_08_continua(m):
    op = Operadora()
    at = m.Atendimento(m.Banco(), op)
    op.cair('depois')
    t, _ = at.pedir_reembolso(LUMINARIA, 101)
    at.retomar(t)
    assert at.situacao(t)['status'] == 'reembolsado' and pagos(op, 101) == 1, op.pagamentos


def teste_pausa_fica_na_trilha(m):
    at = m.Atendimento(m.Banco(), Operadora())
    t, _ = at.pedir_reembolso(DELA, 29)
    assert len(passagens(at.trilha_de(t), 'aprovar', 'pausou')) == 1, curta(at.trilha_de(t))


def teste_decisao_fica_na_trilha_com_quem_e_quando(m):
    at = m.Atendimento(m.Banco(), Operadora(), relogio(NOVE_HORAS))
    t, _ = at.pedir_reembolso(DELA, 29)
    at.decidir(t, ANA, True)
    decisoes = passagens(at.trilha_de(t), 'servidor', 'decisão')
    assert len(decisoes) == 1 and ANA in decisoes[0]['detalhe'], curta(at.trilha_de(t))
    assert decisoes[0]['quando'] == NOVE_HORAS, decisoes[0]['quando']
    assert len(passagens(at.trilha_de(t), 'aprovar', 'começou')) == 2, curta(at.trilha_de(t))  # a pausa roda o nó de novo


def teste_decisao_recusada_fica_na_trilha(m):
    at = m.Atendimento(m.Banco(), Operadora())
    t, _ = at.pedir_reembolso(DELA, 29)
    assert at.decidir(t, DANIELA, True) == m.SO_FINANCEIRO
    recusadas = passagens(at.trilha_de(t), 'servidor', 'decisão recusada')
    assert len(recusadas) == 1 and DANIELA in recusadas[0]['detalhe'], curta(at.trilha_de(t))
    assert at.situacao(t)['esperando'], at.situacao(t)


def teste_queda_e_cada_tentativa_ficam_na_trilha(m):
    op = Operadora()
    at = m.Atendimento(m.Banco(), op)
    op.cair('depois')
    t, _ = at.pedir_reembolso(LUMINARIA, 101)
    at.retomar(t)
    trilha = at.trilha_de(t)
    caiu = passagens(trilha, 'reembolsar', 'caiu')
    assert len(passagens(trilha, 'reembolsar', 'começou')) == 2, curta(trilha)
    assert len(caiu) == 1 and caiu[0]['detalhe'].startswith('ForaDoAr'), curta(trilha)
    assert nos_que_terminaram(trilha) == ['preparar', 'reembolsar'], curta(trilha)


def teste_erro_que_nao_e_queda_fica_na_trilha(m):
    at = m.Atendimento(m.Banco(), Operadora())
    t = pedir_sem_cobranca(at)
    caiu = passagens(at.trilha_de(t), 'reembolsar', 'caiu')
    assert len(caiu) == 1 and caiu[0]['detalhe'].startswith('Recusado'), curta(at.trilha_de(t))


def teste_incompletos_diz_onde_cada_um_parou(m):
    op = Operadora()
    at = m.Atendimento(m.Banco(), op)
    at.pedir_reembolso('Cliente 0098', 52)  # 79,90: termina
    at.pedir_reembolso(DELA, 29)  # espera o financeiro
    op.cair('antes')
    at.pedir_reembolso(LUMINARIA, 101)  # a operadora cai
    pedir_sem_cobranca(at)  # a operadora recusa
    lista = {i['pedido']: i for i in at.incompletos()}
    resumo = {p: (i['onde'], i['motivo']) for p, i in lista.items()}
    assert sorted(lista) == [4, 29, 101], resumo
    assert [lista[p]['onde'] for p in (29, 101, 4)] == ['aprovar', 'reembolsar', 'reembolsar'], resumo
    assert 'esperando' in lista[29]['motivo'] and 'retomar' in lista[101]['motivo'], resumo
    assert 'Recusado' in lista[4]['motivo'] and 'pessoa' in lista[4]['motivo'], resumo


def teste_terca_reproduzida_bate_com_a_exportada(m):
    op = Operadora()
    at = m.Atendimento(m.Banco(), op)
    pedir_sem_cobranca(at)
    op.cair('antes')
    at.pedir_reembolso(LUMINARIA, 101)
    try:
        for t in at.parados():  # o retomar da noite de terça
            at.retomar(t)
    except Recusado:
        pass
    assert comparar(trilha_toda(at), ler_trilha(TERCA)) == [], comparar(trilha_toda(at), ler_trilha(TERCA))
    assert extrato(op) == ler_extrato(EXTRATO_TERCA), extrato(op)


def teste_noite_nao_para_no_primeiro_erro(m):
    op = Operadora()
    at = m.Atendimento(m.Banco(), op)
    quatro = pedir_sem_cobranca(at)
    op.cair('antes')
    luminaria, _ = at.pedir_reembolso(LUMINARIA, 101)
    at.retomar_parados()
    assert at.situacao(luminaria)['status'] == 'reembolsado' and pagos(op, 101) == 1, op.pagamentos
    assert len(passagens(at.trilha_de(quatro), 'reembolsar', 'começou')) == 1, curta(at.trilha_de(quatro))
    assert [i['pedido'] for i in at.incompletos()] == [4], [i['pedido'] for i in at.incompletos()]


TESTES = [teste_reembolso_direto_passa_pelos_nos_na_ordem, teste_rejeicao_passa_pelo_rejeitar,
          teste_cada_thread_tem_a_sua_trilha, teste_trilha_continua_depois_do_reinicio,
          teste_retomada_da_aula_08_continua, teste_pausa_fica_na_trilha,
          teste_decisao_fica_na_trilha_com_quem_e_quando, teste_decisao_recusada_fica_na_trilha,
          teste_queda_e_cada_tentativa_ficam_na_trilha, teste_erro_que_nao_e_queda_fica_na_trilha,
          teste_incompletos_diz_onde_cada_um_parou, teste_terca_reproduzida_bate_com_a_exportada,
          teste_noite_nao_para_no_primeiro_erro]

if __name__ == '__main__':
    sys.exit(rodar_testes(TESTES, sys.argv[1] if len(sys.argv) > 1 else 'servidor.py', sys.argv[2:]))
