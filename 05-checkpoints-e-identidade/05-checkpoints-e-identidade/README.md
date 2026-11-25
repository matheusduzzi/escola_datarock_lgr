# 05. Checkpoints e identidade

Os arquivos da aula. Rode os comandos de dentro dessa pasta. Os pedidos vêm da pasta `dados/loja` do kit.

| Arquivo | O que é |
|---|---|
| `demonstracao.py` | O atendimento com a conversa salva, em duas versões: a proposta do app (`sem-contrato`) e o contrato da aula (`com-contrato`). Tem um nó só, com regras fixas no lugar do modelo de linguagem. |
| `meu-contrato.md` | O contrato da aula, para você mudar no exercício, e a tabela dos oito casos. |
| `requirements.txt` | As versões usadas na aula. |

## Instalar o LangGraph

Em 13 de novembro de 2026, as versões mais novas no PyPI eram o LangGraph 1.2.21 e o langchain-core 1.8.0. O langchain-core 1.8.0 pede Python 3.11 ou mais novo. Se você já criou o ambiente na aula 04, pode usar o mesmo.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No Windows, troque as duas primeiras linhas por `py -m venv .venv` e `.venv\Scripts\activate`. Com o ambiente ativo, os comandos abaixo usam o Python dele. Nada aqui chama um modelo de linguagem de verdade nem precisa de chave ou internet depois da instalação.

## Comandos

```bash
python3 demonstracao.py sem-contrato
python3 demonstracao.py com-contrato
```

Sem o nome da versão, o programa mostra como usar e sai com código 1. As conversas ficam no `InMemorySaver`, na memória do Python: cada vez que você roda, elas começam do zero.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
