# 10. Defesa do atendimento

Os arquivos da aula. Rode os comandos de dentro dessa pasta. Os pedidos e as mensagens vêm da pasta `dados/loja` do kit.

| Arquivo | O que é |
|---|---|
| `regras.py` | As regras de texto: para que rota vai cada mensagem e qual é o número do pedido. Só usa a biblioteca padrão. |
| `sistema.py` | O sistema de pedidos da loja, igual ao da aula 03. Você escolhe quantas consultas falham. Só usa a biblioteca padrão. |
| `pagamentos.py` | O sistema de pagamentos. Grava cada reembolso com uma chave e cai quando você pede, antes ou depois de gravar. Só usa a biblioteca padrão. |
| `atendimento.py` | O grafo do atendimento que vai para a defesa. |
| `versao_do_colega.py` | O grafo que um colega quer ligar no lugar do seu. |
| `testes.py` | O que os testes usam: carregar um grafo, abrir uma conversa com `thread_id` próprio, responder pelo financeiro e continuar depois de uma falha. |
| `testar_defesa.py` | Os testes da defesa: execução normal, negação, retomada depois de falha e as 59 mensagens. |
| `defesa.py` | As três execuções passo a passo, para mostrar na defesa. |
| `meus_testes.py` | O começo dos seus testes do exercício, com um teste de exemplo. |
| `requirements.txt` | As versões do LangGraph usadas na aula. |
| `minha-defesa.md` | A folha da sua defesa: o grafo, as execuções, os testes e os limites. |

## Instalar o LangGraph

O `regras.py`, o `sistema.py` e o `pagamentos.py` rodam com o Python 3.9 ou mais novo, sem instalar nada. O resto usa o LangGraph. Em 13 de novembro de 2026, a versão mais nova no PyPI era a 1.2.21, e ela pede Python 3.10 ou mais novo. Ela instala junto o `langgraph-checkpoint`, que traz o `InMemorySaver`.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No Windows, troque as duas primeiras linhas por `py -m venv .venv` e `.venv\Scripts\activate`. Com o ambiente ativo, os comandos abaixo usam o Python dele. Nada aqui chama um modelo de linguagem nem precisa de chave ou internet depois da instalação.

## Comandos

```bash
python3 regras.py
python3 defesa.py normal
python3 defesa.py negacao
python3 defesa.py retomada
python3 testar_defesa.py
python3 testar_defesa.py versao_do_colega.py
```

Para o financeiro responder outra coisa na negação, use `--resposta`, por exemplo `python3 defesa.py negacao --resposta "não"`.

Para o exercício, escreva os seus testes no `meus_testes.py` e rode:

```bash
python3 meus_testes.py
python3 meus_testes.py uma_copia_quebrada.py
```

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
