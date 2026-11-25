# 06. Memória por thread

Os arquivos da aula. Rode os comandos de dentro dessa pasta. Os pedidos vêm da pasta `dados/loja` do kit.

| Arquivo | O que é |
|---|---|
| `servidor.py` | O atendimento com a conversa salva, já corrigido: o `Banco` (conversas e tabela de donos) e o `Atendimento` (o servidor, com a porta em toda mensagem). O grafo tem um nó só, com regras fixas no lugar do modelo de linguagem. |
| `versao_do_colega.py` | O servidor do jeito que estava no dia das duas reclamações. |
| `historia.py` | Roda as duas reclamações da coordenadora contra um servidor. |
| `testes.py` | O que os testes usam: carregar um arquivo, contar as fotos de uma conversa, ler as mensagens salvas e rodar uma lista de testes. |
| `testar_memoria.py` | Os 8 testes de continuidade e de isolamento do atendimento. |
| `meus_testes.py` | O começo dos seus testes do exercício, com um teste de exemplo. |
| `requirements.txt` | As versões usadas na aula. |

## Instalar o LangGraph

Em 13 de novembro de 2026, as versões mais novas no PyPI eram o LangGraph 1.2.21 e o langchain-core 1.8.0. O langchain-core 1.8.0 pede Python 3.11 ou mais novo. Se você já criou o ambiente nas aulas 04 ou 05, pode usar o mesmo.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No Windows, troque as duas primeiras linhas por `py -m venv .venv` e `.venv\Scripts\activate`. Com o ambiente ativo, os comandos abaixo usam o Python dele. Nada aqui chama um modelo de linguagem de verdade nem precisa de chave ou internet depois da instalação.

## Comandos

```bash
python3 historia.py versao_do_colega.py
python3 historia.py
python3 testar_memoria.py
python3 testar_memoria.py versao_do_colega.py
python3 testar_memoria.py versao_do_colega.py teste_continua_depois_do_reinicio
```

Com a versão do colega, o `testar_memoria.py` termina em `5 de 8 testes passaram` e sai com código 1. É de propósito: são as falhas que a aula mostra.

As conversas ficam num `InMemorySaver`, na memória do Python. Cada vez que você roda, elas começam do zero. Dentro de um teste, o reinício do servidor é um `Atendimento` novo com o mesmo `Banco`.

Para o exercício, copie o `servidor.py` para `retomar.py`, escreva o `retomar` e rode:

```bash
python3 meus_testes.py
python3 meus_testes.py uma_copia_quebrada.py
python3 testar_memoria.py retomar.py
```

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
