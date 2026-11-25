# Meu mapa do script de trocas

## 1. O que o script sabe

Uma linha para cada variável do `troca_antiga.py` que guarda alguma coisa sobre a mensagem. Mais duas linhas, que no script não têm nome: a instrução que vai para o modelo e a resposta que ele devolve.

| Variável no script | O que guarda | No grafo: chave do estado ou fica dentro do nó? | Qual nó escreve |
|---|---|---|---|
| `texto` | a mensagem do cliente | chave `mensagem` | a entrada, pelo `START` |
| | | | |

## 2. As mensagens que usaram o pedido de outra

Saída de `python3 troca_antiga.py`. Para cada mensagem sem número, o pedido que ela usou e de qual mensagem ele veio.

| Mensagem | Pedido que ela usou | Veio da mensagem |
|---|---|---|
| | | |

## 3. O que muda no grafo

O que o grafo faz com a mensagem sem número, e por quê.

## 4. Os nós e as setas

| De | Vai para |
|---|---|
| START | ler_numero |
| | |

## 5. Saída de `python3 testar_troca.py`

```text

```
