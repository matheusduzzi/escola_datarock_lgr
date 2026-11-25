# 07. Humano no loop

Os arquivos da aula. Rode os comandos de dentro dessa pasta. Os pedidos vêm da pasta `dados/loja` do kit.

| Arquivo | O que é |
|---|---|
| `servidor.py` | O reembolso com a pausa para o financeiro, já corrigido: o `Banco` (reembolsos salvos, donos e pagamentos) e o `Atendimento` (o servidor, com o `pedir_reembolso` e o `decidir`). Sem modelo de linguagem. |
| `versao_do_colega.py` | O servidor do jeito que estava no dia das duas reclamações do financeiro. |
| `pausa.py` | Um nó que pausa, com um `print` na primeira linha para ver quando ele roda. |
| `historia.py` | Roda as duas reclamações do financeiro contra um servidor. |
| `testes.py` | O que os testes usam: carregar um arquivo, um relógio parado, contar pagamentos e rodar uma lista de testes. |
| `testar_aprovacao.py` | Os 10 testes da pausa e da decisão. |
| `meus_testes.py` | O começo dos seus testes do exercício, com um teste de exemplo. |
| `requirements.txt` | As versões usadas na aula. |

## Instalar o LangGraph

Em 13 de novembro de 2026, as versões mais novas no PyPI eram o LangGraph 1.2.21 e o langchain-core 1.8.0. O langchain-core 1.8.0 pede Python 3.11 ou mais novo. Se você já criou o ambiente nas aulas 04 a 06, pode usar o mesmo.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Se o `python3 --version` mostrar um Python mais velho que o 3.11, crie o ambiente com o Python novo, por exemplo `python3.11 -m venv .venv`. No Windows, troque as duas primeiras linhas por `py -3.11 -m venv .venv` e `.venv\Scripts\activate`. Com o ambiente ativo, os comandos abaixo usam o Python dele. Nada aqui chama um modelo de linguagem nem precisa de chave ou internet depois da instalação.

## Comandos

```bash
python3 pausa.py
python3 pausa.py engolida
python3 historia.py versao_do_colega.py
python3 historia.py
python3 testar_aprovacao.py
python3 testar_aprovacao.py versao_do_colega.py
```

Com a versão do colega, o `testar_aprovacao.py` termina em `5 de 10 testes passaram` e sai com código 1. É de propósito: são as falhas que a aula mostra.

Os reembolsos ficam num `InMemorySaver`, na memória do Python. Cada vez que você roda, eles começam do zero. Dentro de um teste, o reinício do servidor é um `Atendimento` novo com o mesmo `Banco`. Os pagamentos do kit são uma lista no `Banco`: nenhum dinheiro sai de verdade.

Para o exercício, copie o `servidor.py` para `dupla.py`, mude a regra e rode:

```bash
python3 meus_testes.py
python3 meus_testes.py uma_copia_quebrada.py
python3 testar_aprovacao.py dupla.py
```

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
