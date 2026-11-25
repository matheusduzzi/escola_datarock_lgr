"""Atendimento do jeito que estava no dia dos dois cancelamentos errados.

A regra está só na descrição da ferramenta, que o modelo lê. O código cancela o que o modelo pedir.

    python3 versao_do_colega.py "Cliente 0036" "Quero cancelar o pedido 109"
"""
import sys

from langchain_core.tools import tool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from modelo_falso import ModeloFalsoLoja
from regras import STATUS
from sistema import SistemaPedidos


class Estado(MessagesState):
    cliente: str


def criar_ferramentas(sistema):
    @tool
    def consultar_pedido(id_pedido: int) -> str:
        """Consulta o status e a previsão de entrega de um pedido pelo número."""
        pedido = sistema.buscar(id_pedido)
        if pedido is None:
            return f'Não achei o pedido {id_pedido}.'
        return (f"O pedido {id_pedido} está {STATUS[pedido['status']]}. "
                f"Previsão de entrega: {pedido['previsao_entrega']}.")

    @tool
    def cancelar_pedido(id_pedido: int) -> str:
        """Cancela um pedido. Só cancele pedidos do próprio cliente que ainda não saíram da loja."""
        sistema.cancelar(id_pedido)
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


if __name__ == '__main__':
    from atendimento import mostrar
    cliente = sys.argv[1] if len(sys.argv) > 1 else 'Cliente 0036'
    mensagem = sys.argv[2] if len(sys.argv) > 2 else 'Quero cancelar o pedido 40'
    sistema = SistemaPedidos()
    final = montar_grafo(sistema).invoke({'messages': [('user', mensagem)], 'cliente': cliente},
                                         {'recursion_limit': 10})
    mostrar(final, sistema)
