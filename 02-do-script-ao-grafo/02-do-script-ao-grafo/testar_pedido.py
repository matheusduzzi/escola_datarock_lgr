"""Testes do grafo do pedido: o mesmo que o script fazia, com o modelo falso.

    python3 testar_pedido.py                       testa pedido_grafo.py
    python3 testar_pedido.py versao_do_colega.py   testa outro arquivo com montar_grafo
"""
import sys

from atendimento_antigo import (PALAVRAS_PEDIDO, PALAVRAS_REEMBOLSO, PALAVRAS_TROCA, atender, ler_mensagens,
                                normalizar, tem)
from testes import RESPOSTA, rodar, rodar_testes


def vai_para_o_pedido(texto):
    """As mensagens que o script antigo manda para o bloco do pedido."""
    t = normalizar(texto)
    return not tem(t, PALAVRAS_REEMBOLSO) and not tem(t, PALAVRAS_TROCA) and tem(t, PALAVRAS_PEDIDO)


def resposta_do_script(estado):
    """Monta, só com o estado do grafo, a frase que o script antigo respondia."""
    if estado.get('consulta') == 'achou':
        return f"O pedido {estado['numero']} está {estado['pedido']['status']}."
    if estado.get('consulta') == 'sem_numero':
        return 'Qual é o número do pedido?'
    if estado.get('consulta') == 'nao_achou':
        return f"Não achei o pedido {estado['numero']}."
    return None


def teste_tres_nos_na_ordem(m):
    final, _, _ = rodar(m, 'O pedido 84 já foi enviado?')
    assert final['caminho'] == ['ler_numero', 'consultar', 'redigir'], final['caminho']


def teste_mesmo_que_o_script(m):
    mensagens = [x['texto'] for x in ler_mensagens() if vai_para_o_pedido(x['texto'])]
    diferentes = []
    for texto in mensagens:
        final, _, _ = rodar(m, texto)
        if resposta_do_script(final) != atender(texto):
            diferentes.append(texto)
    print(f'       {len(mensagens)} mensagens do caminho do pedido, {len(mensagens) - len(diferentes)} iguais ao script')
    assert not diferentes, diferentes[0]


def teste_modelo_recebe_os_fatos(m):
    final, modelo, _ = rodar(m, 'O pedido 84 já foi enviado?')
    assert len(modelo.chamadas) == 1, len(modelo.chamadas)
    for fato in ('Pedido 84', 'Luminária de mesa', 'em_separacao', '2026-09-20'):
        assert fato in modelo.chamadas[0], fato
    assert final['resposta'] == RESPOSTA, final['resposta']


def teste_sem_numero_nao_consulta(m):
    final, modelo, sistema = rodar(m, 'Onde está a ENTREGA?')
    assert final['consulta'] == 'sem_numero', final.get('consulta')
    assert sistema.chamadas == 0, sistema.chamadas
    assert len(modelo.chamadas) == 1, len(modelo.chamadas)
    assert 'Peça o número' in modelo.chamadas[0], modelo.chamadas[0]


def teste_pedido_que_nao_existe(m):
    final, modelo, _ = rodar(m, 'Cadê o meu pedido 999?')
    assert final['consulta'] == 'nao_achou', final.get('consulta')
    assert 'pedido' not in final, final.get('pedido')
    assert len(modelo.chamadas) == 1, len(modelo.chamadas)
    assert '999 não existe' in modelo.chamadas[0], modelo.chamadas[0]


def teste_sistema_fora_do_ar(m):
    final, modelo, sistema = rodar(m, 'O pedido 84 já foi enviado?', fora_do_ar=True)
    assert final['consulta'] == 'falhou', final.get('consulta')
    assert sistema.chamadas == 1, sistema.chamadas
    assert len(modelo.chamadas) == 1, len(modelo.chamadas)
    assert 'não respondeu' in modelo.chamadas[0], modelo.chamadas[0]


TESTES = [teste_tres_nos_na_ordem, teste_mesmo_que_o_script, teste_modelo_recebe_os_fatos,
          teste_sem_numero_nao_consulta, teste_pedido_que_nao_existe, teste_sistema_fora_do_ar]

if __name__ == '__main__':
    sys.exit(rodar_testes(TESTES, sys.argv[1] if len(sys.argv) > 1 else 'pedido_grafo.py'))
