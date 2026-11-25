"""Os testes da pausa e da decisão do reembolso.

    python3 testar_aprovacao.py                              testa servidor.py
    python3 testar_aprovacao.py versao_do_colega.py          testa outro arquivo
    python3 testar_aprovacao.py servidor.py nome_do_teste    roda só esse teste

Aprovação e rejeição andam juntas: o dinheiro só sai com um sim do financeiro, sai uma vez, e
cada decisão fica anotada com quem e quando.
"""
import sys

from testes import ANA, BRUNO, DELA, DELE, NOVE_HORAS, TARDE, pagos, relogio, rodar_testes


def teste_ate_200_reembolsa_sem_pausar(m):
    banco = m.Banco()
    at = m.Atendimento(banco)
    for cliente, pedido in (('Cliente 0143', 101), ('Cliente 0271', 42)):  # 99,90 e 200,00 cravados
        t, _ = at.pedir_reembolso(cliente, pedido)
        s = at.situacao(t)
        assert (s['status'], s['esperando']) == ('reembolsado', False), (pedido, s)
        assert pagos(banco, pedido) == 1, (pedido, banco.pagamentos)


def teste_acima_de_200_pausa_sem_pagar(m):
    banco = m.Banco()
    at = m.Atendimento(banco)
    t, resposta = at.pedir_reembolso(DELA, 29)
    pausa = at.grafo.get_state(m.config(t)).tasks[0].interrupts[0].value
    assert at.situacao(t)['esperando'], resposta
    assert (pausa['id_pedido'], pausa['valor']) == (29, 349.9), pausa
    assert pagos(banco, 29) == 0, banco.pagamentos


def teste_aprovado_paga_uma_vez(m):
    banco = m.Banco()
    at = m.Atendimento(banco, relogio(NOVE_HORAS))
    t, _ = at.pedir_reembolso(DELA, 29)
    at.decidir(t, ANA, True)
    assert at.situacao(t)['status'] == 'reembolsado', at.situacao(t)
    assert pagos(banco, 29) == 1, banco.pagamentos


def teste_rejeitado_nao_paga(m):
    banco = m.Banco()
    at = m.Atendimento(banco, relogio(NOVE_HORAS))
    t, _ = at.pedir_reembolso(DELA, 29)
    at.decidir(t, ANA, False)
    assert at.situacao(t)['status'] == 'rejeitado', at.situacao(t)
    assert pagos(banco, 29) == 0, banco.pagamentos


def teste_decisao_anotada_com_quem_e_quando(m):
    at = m.Atendimento(m.Banco(), relogio(NOVE_HORAS))
    dela, _ = at.pedir_reembolso(DELA, 29)
    dele, _ = at.pedir_reembolso(DELE, 44)
    at.decidir(dela, ANA, True)
    at.decidir(dele, BRUNO, False)
    assert at.situacao(dela)['decisoes'] == [{'resultado': 'aprovado', 'quem': ANA, 'quando': NOVE_HORAS}], \
        at.situacao(dela)
    assert at.situacao(dele)['decisoes'] == [{'resultado': 'rejeitado', 'quem': BRUNO, 'quando': NOVE_HORAS}], \
        at.situacao(dele)


def teste_retoma_depois_do_reinicio(m):
    banco = m.Banco()
    antes = m.Atendimento(banco, relogio(NOVE_HORAS))
    dela, _ = antes.pedir_reembolso(DELA, 29)
    dele, _ = antes.pedir_reembolso(DELE, 44)
    depois = m.Atendimento(banco, relogio(TARDE))  # o servidor reinicia; o banco continua
    depois.decidir(dele, ANA, True)
    assert depois.situacao(dele)['status'] == 'reembolsado', depois.situacao(dele)
    assert depois.situacao(dela)['esperando'], 'a outra pausa precisa continuar esperando'
    assert (pagos(banco, 44), pagos(banco, 29)) == (1, 0), banco.pagamentos
    quando = [d.get('quando') for d in depois.situacao(dele)['decisoes']]
    assert quando == [TARDE], f'a hora anotada precisa ser a da decisão: {quando}'


def teste_so_o_financeiro_decide(m):
    banco = m.Banco()
    at = m.Atendimento(banco)
    t, _ = at.pedir_reembolso(DELA, 29)
    antes = list(banco.pagamentos)
    resposta = at.decidir(t, DELA, True)  # a própria cliente tenta aprovar
    assert resposta == m.SO_FINANCEIRO, resposta
    assert at.situacao(t)['esperando'] and banco.pagamentos == antes, at.situacao(t)


def teste_so_um_sim_aprova(m):
    at = m.Atendimento(m.Banco())
    for resposta in ('sim', 1, None):
        t, _ = at.pedir_reembolso(DELA, 29)
        at.decidir(t, ANA, resposta)
        assert at.situacao(t)['status'] == 'rejeitado', (resposta, at.situacao(t))


def teste_nao_decide_duas_vezes(m):
    banco = m.Banco()
    at = m.Atendimento(banco, relogio(NOVE_HORAS))
    t, _ = at.pedir_reembolso(DELA, 29)
    at.decidir(t, ANA, False)
    antes = (at.situacao(t), list(banco.pagamentos))
    resposta = at.decidir(t, BRUNO, True)  # alguém aprova depois da rejeição
    assert resposta == m.NADA_ESPERANDO, resposta
    assert (at.situacao(t), banco.pagamentos) == antes, at.situacao(t)
    assert at.decidir('nao-existe', ANA, True) == m.NADA_ESPERANDO


def teste_55_pausam_e_65_saem_direto(m):
    at = m.Atendimento(m.Banco())
    pausaram = sum(at.situacao(at.pedir_reembolso(p['cliente'], n)[0])['esperando'] for n, p in m.PEDIDOS.items())
    assert (pausaram, len(m.PEDIDOS) - pausaram) == (55, 65), pausaram


TESTES = [teste_ate_200_reembolsa_sem_pausar, teste_acima_de_200_pausa_sem_pagar, teste_aprovado_paga_uma_vez,
          teste_rejeitado_nao_paga, teste_decisao_anotada_com_quem_e_quando, teste_retoma_depois_do_reinicio,
          teste_so_o_financeiro_decide, teste_so_um_sim_aprova, teste_nao_decide_duas_vezes,
          teste_55_pausam_e_65_saem_direto]

if __name__ == '__main__':
    arquivo = sys.argv[1] if len(sys.argv) > 1 else 'servidor.py'
    sys.exit(rodar_testes(TESTES, arquivo, sys.argv[2:]))
