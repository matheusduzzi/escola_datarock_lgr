# 03. Arestas condicionais

Os arquivos da aula. Rode os comandos de dentro dessa pasta. Os pedidos e as mensagens vêm da pasta `dados/loja` do kit.

| Arquivo | O que é |
|---|---|
| `regras.py` | As regras de texto: para que rota vai cada mensagem e qual é o número do pedido. Só usa a biblioteca padrão. |
| `sistema.py` | O sistema de pedidos da loja. Você escolhe quantas consultas falham antes de ele responder. Só usa a biblioteca padrão. |
| `atendimento.py` | O grafo do atendimento com as duas arestas condicionais, já corrigido. |
| `versao_do_colega.py` | O grafo do jeito que estava no dia em que o atendimento travou. |
| `testes.py` | O que os testes usam: carregar um grafo, rodar uma mensagem com limite de passos e mostrar o resultado. |
| `testar_atendimento.py` | Os testes de caminhos e de término do atendimento. |
| `meus_testes.py` | O começo dos seus testes do exercício, com um teste de exemplo. |
| `requirements.txt` | As versões do LangGraph usadas na aula. |

## Instalar o LangGraph

O `regras.py` e o `sistema.py` rodam com o Python 3.9 ou mais novo, sem instalar nada. O resto usa o LangGraph. Em 13 de novembro de 2026, a versão mais nova no PyPI era a 1.2.21, e ela pede Python 3.10 ou mais novo.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No Windows, troque as duas primeiras linhas por `py -m venv .venv` e `.venv\Scripts\activate`. Com o ambiente ativo, os comandos abaixo usam o Python dele. Nada aqui chama um modelo de linguagem nem precisa de chave ou internet depois da instalação.

## Comandos

```bash
python3 regras.py
python3 atendimento.py "O pedido 84 já foi enviado?"
python3 testar_atendimento.py
python3 testar_atendimento.py versao_do_colega.py
```

Para o exercício, copie o `atendimento.py` para `cancelamento.py`, faça as mudanças e rode:

```bash
python3 meus_testes.py
python3 meus_testes.py uma_copia_quebrada.py
```

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
