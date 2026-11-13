# 01. Grafo e máquina de estados

Os arquivos da aula. Rode os comandos de dentro dessa pasta. Os pedidos e as mensagens vêm da pasta `dados/loja` do kit.

| Arquivo | O que é |
|---|---|
| `atendimento_antigo.py` | O atendimento do jeito que ele era: um script com um `if` atrás do outro. Você desenha o que ele faz. Não precisa corrigir. |
| `meu-diagrama.md` | O começo da sua entrega do exercício, com o diagrama do atendimento da aula. |

## Do que você precisa

Python 3.9 ou mais novo. O script só usa a biblioteca padrão: não precisa instalar nada. O LangGraph entra na aula 02.

Para o desenho, papel e caneta servem. Qualquer ferramenta de desenho também.

## Comandos

```bash
python3 atendimento_antigo.py
python3 atendimento_antigo.py "Bom dia"
python3 atendimento_antigo.py "Quero reembolso do pedido 86"
```

O primeiro roda as 59 mensagens do kit e mostra quantas ficaram sem resposta. Os outros rodam uma mensagem só. No Windows, troque `python3` por `py`.

O sistema de pedidos do kit nunca cai. Por isso o script não trava quando você roda. O defeito da consulta que tenta de novo para sempre está no código, e é o desenho que mostra.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
