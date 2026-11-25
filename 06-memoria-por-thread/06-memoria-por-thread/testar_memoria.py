"""Os testes de continuidade e de isolamento do atendimento.

    python3 testar_memoria.py                          testa servidor.py
    python3 testar_memoria.py versao_do_colega.py      testa outro arquivo
    python3 testar_memoria.py servidor.py nome_do_teste    roda só esse teste

Continuidade: a dona volta e o atendimento lembra. Isolamento: ninguém mais entra, e o banco
da conversa dela não muda.
"""
import sys

from testes import DELA, DELE, RECUSA, contar_fotos, rodar_testes, textos

PEDIDO_7 = 'Pelo que conversamos, o seu último pedido é o 7. Valor: 850,00.'


# Continuidade

def teste_continua_na_mesma_conversa(m):
    at = m.Atendimento(m.Banco())
    t = at.nova_conversa(DELA)
    at.enviar(t, DELA, 'Quero saber do pedido 7')
    resposta = at.enviar(t, DELA, 'Qual o valor do meu último pedido?')
    assert resposta == PEDIDO_7, resposta


def teste_continua_depois_do_reinicio(m):
    banco = m.Banco()
    antes = m.Atendimento(banco)
    t = antes.nova_conversa(DELA)
    antes.enviar(t, DELA, 'Quero saber do pedido 7')
    depois = m.Atendimento(banco)  # o servidor reinicia; o banco continua
    resposta = depois.enviar(t, DELA, 'Qual o valor do meu último pedido?')
    assert resposta == PEDIDO_7, resposta


def teste_conversa_nova_comeca_vazia(m):
    at = m.Atendimento(m.Banco())
    primeira = at.nova_conversa(DELA)
    at.enviar(primeira, DELA, 'Quero saber do pedido 7')
    segunda = at.nova_conversa(DELA)
    assert segunda != primeira, segunda
    resposta = at.enviar(segunda, DELA, 'Qual o valor do meu último pedido?')
    assert resposta.startswith('Achei o seu último pedido. O pedido 101'), resposta


# Isolamento

def teste_outro_cliente_nao_entra_pelo_codigo(m):
    at = m.Atendimento(m.Banco())
    t = at.nova_conversa(DELA)
    at.enviar(t, DELA, 'Quero saber do pedido 7')
    fotos, salvas = contar_fotos(at, t), textos(at, t)
    resposta = at.enviar(t, DELE, 'Qual o valor do meu último pedido?')
    assert resposta == RECUSA, resposta
    assert (contar_fotos(at, t), textos(at, t)) == (fotos, salvas), textos(at, t)[-2:]


def teste_conversa_nova_depois_do_reinicio_nao_cai_em_outra(m):
    banco = m.Banco()
    antes = m.Atendimento(banco)
    dela = antes.nova_conversa(DELA)
    antes.enviar(dela, DELA, 'Quero saber do pedido 7')
    depois = m.Atendimento(banco)
    dele = depois.nova_conversa(DELE)
    assert dele != dela, f'o código novo é o da conversa dela: {dele}'
    assert banco.donos[dela] == DELA, banco.donos[dela]
    resposta = depois.enviar(dele, DELE, 'Qual o valor do meu último pedido?')
    assert resposta.startswith('Achei o seu último pedido. O pedido 10,'), resposta


def teste_duas_conversas_ao_mesmo_tempo(m):
    at = m.Atendimento(m.Banco())
    dela, dele = at.nova_conversa(DELA), at.nova_conversa(DELE)
    at.enviar(dela, DELA, 'Quero saber do pedido 7')
    at.enviar(dele, DELE, 'Quero saber do pedido 10')
    assert at.enviar(dela, DELA, 'Qual o valor do meu último pedido?') == PEDIDO_7
    resposta = at.enviar(dele, DELE, 'Qual o valor do meu último pedido?')
    assert resposta == 'Pelo que conversamos, o seu último pedido é o 10. Valor: 129,00.', resposta
    assert not any('pedido 10' in x for x in textos(at, dela)), textos(at, dela)
    assert not any('pedido 7' in x for x in textos(at, dele)), textos(at, dele)


def teste_cliente_nao_fica_no_estado(m):
    at = m.Atendimento(m.Banco())
    t = at.nova_conversa(DELA)
    at.enviar(t, DELA, 'Quero saber do pedido 7')
    chaves = set(at.grafo.get_state(m.config(t)).values)
    assert chaves == {'messages'}, chaves


def teste_conversa_apagada_nao_abre(m):
    at = m.Atendimento(m.Banco())
    dela, dele = at.nova_conversa(DELA), at.nova_conversa(DELE)
    at.enviar(dela, DELA, 'Quero saber do pedido 7')
    at.enviar(dele, DELE, 'Quero saber do pedido 10')
    assert at.apagar(dela, DELE) is False and contar_fotos(at, dela) == 3
    assert at.apagar(dela, DELA) is True
    assert contar_fotos(at, dela) == 0 and dela not in at.banco.donos
    assert contar_fotos(at, dele) == 3, contar_fotos(at, dele)
    resposta = at.enviar(dela, DELA, 'Qual o valor do meu último pedido?')
    assert resposta == RECUSA and contar_fotos(at, dela) == 0, (resposta, contar_fotos(at, dela))


TESTES = [teste_continua_na_mesma_conversa, teste_continua_depois_do_reinicio,
          teste_conversa_nova_comeca_vazia, teste_outro_cliente_nao_entra_pelo_codigo,
          teste_conversa_nova_depois_do_reinicio_nao_cai_em_outra, teste_duas_conversas_ao_mesmo_tempo,
          teste_cliente_nao_fica_no_estado, teste_conversa_apagada_nao_abre]

if __name__ == '__main__':
    arquivo = sys.argv[1] if len(sys.argv) > 1 else 'servidor.py'
    sys.exit(rodar_testes(TESTES, arquivo, sys.argv[2:]))
