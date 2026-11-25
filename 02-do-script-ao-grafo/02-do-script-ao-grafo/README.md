# 02. Do script ao grafo

Os arquivos da aula. Rode os comandos de dentro dessa pasta. Os pedidos e as mensagens vêm da pasta `dados/loja` do kit.

| Arquivo | O que é |
|---|---|
| `atendimento_antigo.py` | O mesmo script da aula 01. A aula passa o bloco do pedido para o grafo. |
| `modelo_falso.py` | O modelo falso: responde o que foi escrito antes, no roteiro, e guarda em `chamadas` o que recebeu. |
| `pedido_grafo.py` | O grafo do pedido: três nós, setas fixas e o modelo entrando pelo `montar_grafo`. |
| `versao_do_colega.py` | Uma versão do grafo do pedido que roda sem erro e tem um defeito. |
| `testes.py` | O que os testes usam: carregar um grafo, rodar uma mensagem com o modelo falso e contar as consultas ao sistema. |
| `testar_pedido.py` | Os testes do grafo do pedido, inclusive a comparação com o script nas 19 mensagens de pedido. |
| `troca_antiga.py` | O script de trocas, para o exercício. Não corrija: você passa o que ele faz para um grafo. |
| `testar_troca.py` | Os testes do exercício. Eles leem o seu `troca_grafo.py`. |
| `meu-mapa.md` | O começo da sua entrega do exercício. |
| `requirements.txt` | A versão do LangGraph usada na aula. |

## Instalar o LangGraph

O `atendimento_antigo.py`, o `modelo_falso.py` e o `troca_antiga.py` rodam com o Python 3.9 ou mais novo, sem instalar nada. O resto usa o LangGraph. Em 13 de novembro de 2026, a versão mais nova no PyPI era a 1.2.21, e ela pede Python 3.10 ou mais novo.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

O `requirements.txt` fixa o `langgraph==1.2.21`.

No Windows, troque as duas primeiras linhas por `py -m venv .venv` e `.venv\Scripts\activate`. Com o ambiente ativo, os comandos abaixo usam o Python dele. Nada aqui chama um modelo de verdade nem precisa de chave ou internet depois da instalação.

## Comandos

```bash
python3 atendimento_antigo.py "O pedido 84 já foi enviado?"
python3 pedido_grafo.py "O pedido 84 já foi enviado?"
python3 testar_pedido.py
python3 testar_pedido.py versao_do_colega.py
```

Para o exercício:

```bash
python3 troca_antiga.py
python3 testar_troca.py
```

Antes de você criar o `troca_grafo.py`, o `testar_troca.py` para com `arquivo não encontrado: troca_grafo.py`.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
