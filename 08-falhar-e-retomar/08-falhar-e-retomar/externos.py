"""Os dois serviços de fora da loja: a operadora do cartão e o envio de mensagens.

Os dois são de mentira: nenhum dinheiro sai e nenhuma mensagem sai de verdade. A lista
`pagamentos` da operadora é o dinheiro saindo; a lista `mensagens` do envio é o que a cliente
recebe. Os dois aceitam uma chave, como as operadoras de verdade: a mesma chave na segunda
chamada retorna o que já foi feito, sem fazer de novo.

Para ver uma queda, chame `cair('antes')` ou `cair('depois')` antes da chamada:
'antes' cai sem fazer nada; 'depois' faz o efeito e cai antes de responder. Do lado da loja,
as duas quedas chegam iguais: a exceção ForaDoAr.
"""


class ForaDoAr(Exception):
    """O serviço não respondeu. Não dá para saber, por aqui, se o efeito aconteceu."""


class _Servico:
    def __init__(self):
        self.chamadas = 0
        self._quedas = []
        self._feitos = {}  # chave -> o que foi feito com ela

    def cair(self, quando):
        """A próxima chamada cai: 'antes' de fazer o efeito ou 'depois' de fazer."""
        assert quando in ('antes', 'depois'), quando
        self._quedas.append(quando)

    def _fazer(self, chave, dados, efeito):
        self.chamadas += 1
        queda = self._quedas.pop(0) if self._quedas else None
        if queda == 'antes':
            raise ForaDoAr(f'{self.nome} não respondeu')
        if chave is not None and chave in self._feitos:
            feito = self._feitos[chave]
            if {k: feito[k] for k in dados} != dados:
                raise ValueError(f'a chave {chave} já foi usada com outros dados')
        else:
            feito = efeito(dados)
            if chave is not None:
                self._feitos[chave] = feito
        if queda == 'depois':
            raise ForaDoAr(f'{self.nome} não respondeu')
        return dict(feito)


class Operadora(_Servico):
    """A operadora do cartão. `estornar` devolve o dinheiro do pedido para a cliente."""
    nome = 'a operadora'

    def __init__(self):
        super().__init__()
        self.pagamentos = []  # um item por estorno feito: é o dinheiro saindo

    def estornar(self, id_pedido, valor, chave=None):
        def efeito(dados):
            pagamento = {'id_pagamento': f'E{len(self.pagamentos) + 1:03d}', **dados}
            self.pagamentos.append(pagamento)
            return pagamento
        return self._fazer(chave, {'id_pedido': id_pedido, 'valor': valor}, efeito)


class Mensageiro(_Servico):
    """O envio de mensagens para a cliente. `enviar` manda um texto."""
    nome = 'o envio de mensagens'

    def __init__(self):
        super().__init__()
        self.mensagens = []  # uma por mensagem que chegou na cliente

    def enviar(self, cliente, texto, chave=None):
        def efeito(dados):
            mensagem = {'id_mensagem': f'M{len(self.mensagens) + 1:03d}', **dados}
            self.mensagens.append(mensagem)
            return mensagem
        return self._fazer(chave, {'cliente': cliente, 'texto': texto}, efeito)
