"""Modelo falso: responde o que foi escrito antes, na ordem, e guarda o que recebeu.

Só usa a biblioteca padrão. Não chama nenhum serviço, não precisa de chave nem de internet.

    modelo = ModeloFalso(['Seu pedido 84 está em separação.'])
    modelo.responder('qualquer instrução')   # retorna a 1ª resposta do roteiro
    modelo.chamadas                          # ['qualquer instrução']

Se o grafo chamar o modelo mais vezes do que o roteiro tem respostas, ele para com erro.
"""


class ModeloFalso:
    def __init__(self, roteiro):
        self.roteiro = list(roteiro)
        self.chamadas = []

    def responder(self, instrucao):
        self.chamadas.append(instrucao)
        n = len(self.chamadas)
        if n > len(self.roteiro):
            raise RuntimeError(f'o modelo falso recebeu a chamada {n} e o roteiro só tem {len(self.roteiro)} resposta(s)')
        return self.roteiro[n - 1]
