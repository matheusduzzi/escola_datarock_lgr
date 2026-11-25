"""O script de trocas da Loja Exemplo, do jeito que a equipe de trocas deixou.

Só usa a biblioteca padrão. Rode de dentro dessa pasta:

    python3 troca_antiga.py                                  # as mensagens de troca do kit, na ordem
    python3 troca_antiga.py "Quero trocar o produto do pedido 64"

Quem escreve a resposta é um modelo. Aqui roda com o modelo falso. Não corrija o script: no
exercício você passa o que ele faz para um grafo.
"""
import sys

from atendimento_antigo import (PALAVRAS_REEMBOLSO, PALAVRAS_TROCA, ler_mensagens, normalizar, numero_do_pedido,
                                sistema_consultar, tem)
from modelo_falso import ModeloFalso

ultimo_pedido = None  # o pedido da mensagem anterior, para quando o cliente não manda o número


def situacao_da_troca(pedido):
    if pedido is None:
        return 'sem_pedido'
    if pedido['status'] == 'entregue':
        return 'pode_trocar'
    if pedido['status'] == 'cancelado':
        return 'cancelado'
    return 'nao_entregue'


def instrucao_da_troca(texto, situacao, pedido):
    fato = f"Pedido {pedido['id_pedido']}: {pedido['produto']}, status {pedido['status']}. " if pedido else ''
    return (f'Responda ao cliente da Loja Exemplo sobre a troca, em uma frase. Situação: {situacao}. '
            f'{fato}Mensagem do cliente: {texto}')


def atender_troca(texto, modelo):
    global ultimo_pedido
    numero = numero_do_pedido(texto)
    if numero is not None:
        ultimo_pedido = sistema_consultar(numero)
    situacao = situacao_da_troca(ultimo_pedido)
    return modelo.responder(instrucao_da_troca(texto, situacao, ultimo_pedido))


def eh_troca(texto):
    """As mensagens que o atendimento_antigo.py manda para a troca."""
    t = normalizar(texto)
    return not tem(t, PALAVRAS_REEMBOLSO) and tem(t, PALAVRAS_TROCA)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        modelo = ModeloFalso(['(resposta do modelo falso)'])
        print('resposta:', atender_troca(sys.argv[1], modelo))
        print('instrução para o modelo:', modelo.chamadas[0])
    else:
        trocas = [m for m in ler_mensagens() if eh_troca(m['texto'])]
        for m in trocas:
            atender_troca(m['texto'], ModeloFalso(['(resposta do modelo falso)']))
            pedido = ultimo_pedido['id_pedido'] if ultimo_pedido else '-'
            print(f"{m['id_mensagem']:>3}  {m['texto']!r:52} pedido {pedido:>3}  {situacao_da_troca(ultimo_pedido)}")
        print(f'{len(trocas)} mensagens de troca')
