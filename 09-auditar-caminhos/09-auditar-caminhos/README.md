# 09. Auditar caminhos

Os arquivos da aula. Rode os comandos de dentro dessa pasta. Os pedidos vêm da pasta `dados/loja` do kit.

| Arquivo | O que é |
|---|---|
| `servidor.py` | O reembolso da aula 08 com a trilha: cada nó anota quando começa, termina, pausa ou cai, e o servidor anota o pedido, a decisão, a decisão recusada, o retomar e a resposta. Tem o `trilha_de`, o `incompletos` e o `retomar_parados`. Sem modelo de linguagem. |
| `versao_do_colega.py` | O servidor da aula 08 com o caminho anotado num campo do estado. |
| `externos.py` | A operadora do cartão da aula 08, que agora só estorna pedido que ela cobrou. |
| `exportado/` | A trilha e o extrato da operadora exportados na terça e na quinta. |
| `rastro.py` | Mostra uma trilha exportada, reembolso por reembolso, com o último passo de cada um. |
| `fotos.py` | O que o LangGraph guarda do pedido 4 sem a trilha: o `get_state` e o `get_state_history`. |
| `terca.py` | Roda a noite de terça de novo contra um servidor e compara com a trilha exportada. |
| `testes.py` | O que os testes usam: carregar um servidor, ler e comparar trilhas e extratos, rodar uma lista de testes. |
| `testar_trilha.py` | Os 13 testes da trilha e do retomar da noite. |
| `meus_testes.py` | O começo dos seus testes do exercício, com um teste de exemplo. |
| `minha-investigacao.md` | A folha da sua investigação do exercício. |
| `requirements.txt` | As versões usadas na aula. |

## Instalar o LangGraph

Os comandos da aula rodaram com o LangGraph 1.2.21 e o langchain-core 1.8.0, as mesmas versões das aulas 04 a 08. Em 25 de novembro de 2026, o PyPI já tinha o LangGraph 1.2.24 e o langchain-core 1.8.4; o `requirements.txt` fixa as versões testadas. O langchain-core pede Python 3.11 ou mais novo. Se você já criou o ambiente nas aulas anteriores, pode usar o mesmo.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Se o `python3 --version` mostrar um Python mais velho que o 3.11, crie o ambiente com o Python novo, por exemplo `python3.11 -m venv .venv`. No Windows, troque as duas primeiras linhas por `py -3.11 -m venv .venv` e `.venv\Scripts\activate`. Com o ambiente ativo, os comandos abaixo usam o Python dele. Nada aqui chama um modelo de linguagem nem precisa de chave ou internet depois da instalação.

## Comandos

```bash
python3 rastro.py exportado/trilha-de-terca.jsonl
python3 fotos.py
python3 terca.py versao_do_colega.py
python3 terca.py
python3 terca.py servidor.py conserto
python3 testar_trilha.py
python3 testar_trilha.py versao_do_colega.py
```

Com a versão do colega, o `testar_trilha.py` termina em `5 de 13 testes passaram` e sai com código 1. É de propósito: são as falhas que a aula mostra.

Os reembolsos ficam num `InMemorySaver`, na memória do Python, e a trilha numa lista do mesmo `Banco`. Cada vez que você roda, eles começam do zero. A operadora do kit é uma lista na memória: nenhum dinheiro sai de verdade. Os arquivos de `exportado/` têm uma passagem por linha, em JSON.

Para o exercício, leia a quinta e rode os seus testes:

```bash
python3 rastro.py exportado/trilha-de-quinta.jsonl
python3 meus_testes.py
python3 meus_testes.py servidor.py --trilha copia.jsonl
python3 meus_testes.py servidor.py --extrato copia.csv
```

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
