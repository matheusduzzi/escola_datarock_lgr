"""Testes do exercício: o grafo da troca, no arquivo troca_grafo.py.

    python3 testar_troca.py                   testa troca_grafo.py
    python3 testar_troca.py outra_copia.py    testa outro arquivo com montar_grafo
"""
import re
import sys

import troca_antiga
from atendimento_antigo import ler_mensagens
from modelo_falso import ModeloFalso
from testes import RESPOSTA, rodar, rodar_testes

# O script junta "sem número" e "número que não existe" em sem_pedido. O grafo separa os dois.
DO_SCRIPT = {'sem_numero': 'sem_pedido', 'nao_achou': 'sem_pedido'}


def situacao_do_script(texto):
    """Roda o script com uma mensagem sozinha e lê a situação na instrução que ele mandou ao modelo."""
    troca_antiga.ultimo_pedido = None
    modelo = ModeloFalso([RESPOSTA])
    troca_antiga.atender_troca(texto, modelo)
    return re.search(r'Situação: (\w+)\.', modelo.chamadas[0]).group(1)


def teste_quatro_nos_na_ordem(m):
    final, _, _ = rodar(m, 'Quero trocar o produto do pedido 64')
    assert final['caminho'] == ['ler_numero', 'consultar', 'avaliar', 'redigir'], final['caminho']


def teste_mesmo_que_o_script(m):
    trocas = [x['texto'] for x in ler_mensagens() if troca_antiga.eh_troca(x['texto'])]
    diferentes = []
    for texto in trocas:
        final, _, _ = rodar(m, texto)
        situacao = final.get('situacao')
        if DO_SCRIPT.get(situacao, situacao) != situacao_do_script(texto):
            diferentes.append(texto)
    print(f'       {len(trocas)} mensagens de troca, uma por vez: {len(trocas) - len(diferentes)} iguais ao script')
    assert not diferentes, diferentes[0]


def teste_uma_mensagem_nao_ve_a_outra(m):
    modelo = ModeloFalso([RESPOSTA, RESPOSTA])
    grafo = m.montar_grafo(modelo, troca_antiga.sistema_consultar)
    grafo.invoke({'mensagem': 'Quero trocar o produto do pedido 64'})
    final = grafo.invoke({'mensagem': 'Recebi com defeito, quero devolver'})
    assert final.get('situacao') == 'sem_numero', final.get('situacao')
    assert 'pedido' not in final, final.get('pedido')
    assert len(modelo.chamadas) == 2, len(modelo.chamadas)
    assert 'Pedido 64' not in modelo.chamadas[1], modelo.chamadas[1]


def teste_modelo_recebe_os_fatos(m):
    final, modelo, _ = rodar(m, 'Preciso da devolução do pedido 64')
    assert len(modelo.chamadas) == 1, len(modelo.chamadas)
    for fato in ('Situação: pode_trocar', 'Pedido 64', 'Cafeteira elétrica'):
        assert fato in modelo.chamadas[0], fato
    assert final['resposta'] == RESPOSTA, final['resposta']


def teste_sem_numero_nao_consulta(m):
    final, modelo, sistema = rodar(m, 'Como faço a troca do tamanho?')
    assert final.get('situacao') == 'sem_numero', final.get('situacao')
    assert sistema.chamadas == 0, sistema.chamadas
    assert len(modelo.chamadas) == 1, len(modelo.chamadas)
    assert 'Situação: sem_numero' in modelo.chamadas[0], modelo.chamadas[0]


def teste_pedido_que_nao_existe(m):
    final, modelo, _ = rodar(m, 'Quero trocar o produto do pedido 999')
    assert final.get('situacao') == 'nao_achou', final.get('situacao')
    assert len(modelo.chamadas) == 1, len(modelo.chamadas)
    assert 'Situação: nao_achou' in modelo.chamadas[0], modelo.chamadas[0]


def teste_sistema_fora_do_ar(m):
    final, modelo, sistema = rodar(m, 'Preciso da devolução do pedido 64', fora_do_ar=True)
    assert final.get('situacao') == 'falhou', final.get('situacao')
    assert sistema.chamadas == 1, sistema.chamadas
    assert len(modelo.chamadas) == 1, len(modelo.chamadas)


TESTES = [teste_quatro_nos_na_ordem, teste_mesmo_que_o_script, teste_uma_mensagem_nao_ve_a_outra,
          teste_modelo_recebe_os_fatos, teste_sem_numero_nao_consulta, teste_pedido_que_nao_existe,
          teste_sistema_fora_do_ar]

if __name__ == '__main__':
    sys.exit(rodar_testes(TESTES, sys.argv[1] if len(sys.argv) > 1 else 'troca_grafo.py'))
