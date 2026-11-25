"""Modelo de linguagem falso da Loja Exemplo: segue regras fixas, sem rede e sem chave.

Ele aceita bind_tools e pede ferramentas como um modelo de verdade pediria: uma AIMessage com
tool_calls. Mesma conversa, mesma resposta. Ele não sabe nada de status nem de cliente: pede o
cancelamento de qualquer pedido que o cliente mencionar. Quem barra é a ferramenta.

Regras, nesta ordem, sobre a última mensagem:
1. Resultado de ferramenta com erro: diz que vai passar para uma pessoa.
2. Resultado de ferramenta sem erro: repete o texto da ferramenta para o cliente.
3. "cancelar" e "pedido N", com cancelar_pedido ligada: pede cancelar_pedido(id_pedido=N).
4. Troca ("troca", "trocar", "devolver", "devolução", "defeito") e "pedido N", com abrir_troca
   ligada: pede abrir_troca(id_pedido=N, motivo=...). O motivo é "defeito" se a mensagem fala
   de defeito, "tamanho" se fala de tamanho e "arrependimento" nos outros casos.
5. "pedido N", com consultar_pedido ligada: pede consultar_pedido(id_pedido=N).
6. "pedido N" sem ferramenta: diz que não consegue consultar.
7. Qualquer outra coisa: pede o número do pedido.
"""
import re
import unicodedata
from typing import Any, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import Field

PADRAO_PEDIDO = re.compile(r'pedido\s*(?:n[ºo.]?\s*)?#?(\d+)')
PALAVRAS_TROCA = ('troca', 'trocar', 'devolver', 'devolucao', 'defeito')


def normalizar(texto):
    """Minúsculas e sem acento: "DEVOLUÇÃO" vira "devolucao"."""
    sem_acento = unicodedata.normalize('NFKD', texto or '')
    return ''.join(c for c in sem_acento if not unicodedata.combining(c)).lower()


def _texto(mensagem):
    conteudo = mensagem.content
    if isinstance(conteudo, list):
        conteudo = ' '.join(p.get('text', '') if isinstance(p, dict) else str(p) for p in conteudo)
    return conteudo or ''


class ModeloFalsoLoja(BaseChatModel):
    """Modelo falso com bind_tools. Os nomes das ferramentas ligadas ficam em `ferramentas`."""

    ferramentas: List[str] = Field(default_factory=list)

    @property
    def _llm_type(self):
        return 'modelo-falso-loja'

    def bind_tools(self, tools, **kwargs):
        nomes = [convert_to_openai_tool(t)['function']['name'] for t in tools]
        return self.model_copy(update={'ferramentas': nomes})

    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None,
                  run_manager: Any = None, **kwargs: Any) -> ChatResult:
        return ChatResult(generations=[ChatGeneration(message=self.decidir(messages))])

    def pedir(self, nome, args, messages):
        return AIMessage(content='', tool_calls=[{'name': nome, 'args': args, 'id': f'chamada-{len(messages)}'}])

    def decidir(self, messages):
        ultima = messages[-1]
        if isinstance(ultima, ToolMessage):
            if ultima.status == 'error':
                return AIMessage(content='Não consegui fazer isso agora. Vou passar para uma pessoa da equipe.')
            return AIMessage(content=_texto(ultima))

        texto = normalizar(_texto(ultima))
        numero = PADRAO_PEDIDO.search(texto)
        if numero:
            n = int(numero.group(1))
            if 'cancel' in texto and 'cancelar_pedido' in self.ferramentas:
                return self.pedir('cancelar_pedido', {'id_pedido': n}, messages)
            if any(p in texto for p in PALAVRAS_TROCA) and 'abrir_troca' in self.ferramentas:
                motivo = 'defeito' if 'defeito' in texto else 'tamanho' if 'tamanho' in texto else 'arrependimento'
                return self.pedir('abrir_troca', {'id_pedido': n, 'motivo': motivo}, messages)
            if 'consultar_pedido' in self.ferramentas:
                return self.pedir('consultar_pedido', {'id_pedido': n}, messages)
            return AIMessage(content=f'Não consigo consultar o pedido {n}: estou sem ferramenta.')

        return AIMessage(content='Posso ajudar com pedidos, trocas e cancelamentos. Qual é o número do pedido?')
