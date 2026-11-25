# 04. Ferramentas no grafo

Os arquivos da aula. Rode os comandos de dentro dessa pasta. Os pedidos vêm da pasta `dados/loja` do kit.

| Arquivo | O que é |
|---|---|
| `regras.py` | A regra do cancelamento: que pedido pode ser cancelado e por que não. Só usa a biblioteca padrão. |
| `sistema.py` | O sistema de pedidos da loja. Ele cancela e abre troca do que mandarem, e anota cada mudança em `efeitos`. Só usa a biblioteca padrão. |
| `modelo_falso.py` | O modelo de linguagem do curso: regras fixas, sem rede e sem chave. Pede a ferramenta pelo que a mensagem diz. |
| `atendimento.py` | O atendimento com as ferramentas `consultar_pedido` e `cancelar_pedido`, já corrigido. |
| `versao_do_colega.py` | O atendimento do jeito que estava no dia dos dois cancelamentos errados. |
| `testes.py` | O que os testes usam: carregar um arquivo, conversar, mandar uma decisão escrita na mão e ver o schema. |
| `testar_ferramentas.py` | Os testes da decisão e do efeito do atendimento. |
| `meus_testes.py` | O começo dos seus testes do exercício, com um teste de exemplo. |
| `requirements.txt` | As versões usadas na aula. |

## Instalar o LangGraph

O `regras.py` e o `sistema.py` rodam com o Python 3.9 ou mais novo, sem instalar nada. O resto usa o LangGraph. Em 13 de novembro de 2026, as versões mais novas no PyPI eram o LangGraph 1.2.21 e o langchain-core 1.8.0. O langchain-core 1.8.0 pede Python 3.11 ou mais novo.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No Windows, troque as duas primeiras linhas por `py -m venv .venv` e `.venv\Scripts\activate`. Com o ambiente ativo, os comandos abaixo usam o Python dele. Nada aqui chama um modelo de linguagem de verdade nem precisa de chave ou internet depois da instalação.

## Comandos

```bash
python3 regras.py
python3 atendimento.py "Cliente 0036" "Quero cancelar o pedido 109"
python3 versao_do_colega.py "Cliente 0036" "Quero cancelar o pedido 109"
python3 testar_ferramentas.py
python3 testar_ferramentas.py versao_do_colega.py
```

Para o exercício, copie o `atendimento.py` para `troca.py`, faça as mudanças e rode:

```bash
python3 meus_testes.py
python3 meus_testes.py uma_copia_quebrada.py
python3 testar_ferramentas.py troca.py
```

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
