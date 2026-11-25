"""Atendimento da Loja Exemplo com ferramentas, já corrigido.

O modelo decide qual ferramenta pedir e com que argumentos. O grafo roda a ferramenta.
Dentro da ferramenta de cancelamento, a ordem é: ler o pedido, validar, e só então o efeito.

    python3 atendimento.py "Cliente 0036" "Quero cancelar o pedido 109"
"""
import sys
from typing import Annotated

from langchain_core.tools import tool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, ToolRuntime, tools_condition
from pydantic import Field

from modelo_falso import ModeloFalsoLoja
from regras import STATUS, motivo_para_nao_cancelar
from sistema import SistemaPedidos

# O formato que o modelo precisa mandar: inteiro de verdade (strict) e maior que zero.
IdPedido = Annotated[int, Field(strict=True, gt=0, description='número do pedido, por exemplo 40')]


class Estado(MessagesState):
    cliente: str


def criar_ferramentas(sistema):
    @tool
    def consultar_pedido(id_pedido: IdPedido, runtime: ToolRuntime) -> str:
        """Consulta o status e a previsão de entrega de um pedido do cliente pelo número."""
        cliente = runtime.state['cliente']  # da conversa, não do modelo
        pedido = sistema.buscar(id_pedido)
        if pedido is None or pedido['cliente'] != cliente:
            return 'Não achei: esse pedido não está no seu cadastro.'
        return (f"O pedido {id_pedido} está {STATUS[pedido['status']]}. "
                f"Previsão de entrega: {pedido['previsao_entrega']}.")

    @tool
    def cancelar_pedido(id_pedido: IdPedido, runtime: ToolRuntime) -> str:
        """Cancela um pedido do cliente que ainda não saiu da loja."""
        cliente = runtime.state['cliente']  # da conversa, não do modelo
        pedido = sistema.buscar(id_pedido)                     # 1. ler: não muda nada
        motivo = motivo_para_nao_cancelar(pedido, cliente)     # 2. validar
        if motivo:
            return f'Não cancelei: {motivo}.'
        sistema.cancelar(id_pedido)                            # 3. efeito: só aqui
        return f'Pronto: cancelei o pedido {id_pedido}.'

    return [consultar_pedido, cancelar_pedido]


def montar_grafo(sistema=None, modelo=None):
    sistema = sistema or SistemaPedidos()
    ferramentas = criar_ferramentas(sistema)
    modelo = (modelo or ModeloFalsoLoja()).bind_tools(ferramentas)

    def agente(estado):
        return {'messages': [modelo.invoke(estado['messages'])]}

    g = StateGraph(Estado)
    g.add_node('agente', agente)
    g.add_node('tools', ToolNode(ferramentas))
    g.add_edge(START, 'agente')
    g.add_conditional_edges('agente', tools_condition)
    g.add_edge('tools', 'agente')
    return g.compile()


def mostrar(final, sistema):
    for m in final['messages']:
        print(f'{type(m).__name__:12} {m.tool_calls if getattr(m, "tool_calls", None) else m.content}')
    print('efeitos no sistema:', sistema.efeitos)


if __name__ == '__main__':
    cliente = sys.argv[1] if len(sys.argv) > 1 else 'Cliente 0036'
    mensagem = sys.argv[2] if len(sys.argv) > 2 else 'Quero cancelar o pedido 40'
    sistema = SistemaPedidos()
    final = montar_grafo(sistema).invoke({'messages': [('user', mensagem)], 'cliente': cliente},
                                         {'recursion_limit': 10})
    mostrar(final, sistema)
