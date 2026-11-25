"""O sistema de pagamentos da Loja Exemplo, com a falha que você escolhe.

    Pagamentos()                 responde sempre
    Pagamentos(falha='antes')    a 1ª chamada cai antes de gravar o reembolso
    Pagamentos(falha='depois')   a 1ª chamada grava o reembolso e a confirmação se perde

Cada reembolso leva uma chave. Se a mesma chave chega de novo, o sistema não grava outro
reembolso: ele retorna o que já tinha gravado. Chamada sem chave sempre grava.

Só usa a biblioteca padrão.
"""


class PagamentosFora(Exception):
    """A chamada ao sistema de pagamentos não voltou."""


class Pagamentos:
    def __init__(self, falha=None):
        if falha not in (None, 'antes', 'depois'):
            raise ValueError("falha precisa ser None, 'antes' ou 'depois'")
        self.falha = falha
        self.chamadas = 0
        self.gravados = []  # cada reembolso que saiu de verdade

    def reembolsar(self, chave, id_pedido, valor):
        """Grava o reembolso e retorna o comprovante. Levanta PagamentosFora quando cai."""
        self.chamadas += 1
        primeira = self.chamadas == 1
        if primeira and self.falha == 'antes':
            raise PagamentosFora('a chamada caiu antes de gravar o reembolso')
        if chave is not None:
            for feito in self.gravados:
                if feito['chave'] == chave:
                    return feito
        feito = {'chave': chave, 'id_pedido': id_pedido, 'valor': valor, 'comprovante': len(self.gravados) + 1}
        self.gravados.append(feito)
        if primeira and self.falha == 'depois':
            raise PagamentosFora('o reembolso foi gravado, mas a confirmação não chegou')
        return feito
