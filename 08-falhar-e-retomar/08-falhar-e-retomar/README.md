# 08. Falhar e retomar

Os arquivos da aula. Rode os comandos de dentro dessa pasta. Os pedidos vêm da pasta `dados/loja` do kit.

| Arquivo | O que é |
|---|---|
| `servidor.py` | O reembolso da aula 07 com o estorno que não sai duas vezes, já corrigido: o `Banco` (reembolsos salvos, donos e o registro de efeitos) e o `Atendimento` (o servidor, com `pedir_reembolso`, `decidir`, `retomar` e `parados`). Sem modelo de linguagem. |
| `versao_do_colega.py` | O servidor do jeito que estava no dia do estorno em dobro. |
| `externos.py` | Os dois serviços de fora da loja: a `Operadora` do cartão e o `Mensageiro`, que manda mensagem para a cliente. Os dois aceitam uma chave e sabem cair de propósito. |
| `queda.py` | Um nó que chama a operadora e cai depois de o dinheiro sair, para ver quantas vezes ele roda. |
| `historia.py` | Roda a queda da operadora e o pedido em dobro contra um servidor. |
| `testes.py` | O que os testes usam: carregar um arquivo, um relógio parado, contar estornos e mensagens e rodar uma lista de testes. |
| `testar_retomada.py` | Os 10 testes da queda e da retomada. |
| `meus_testes.py` | O começo dos seus testes do exercício, com um teste de exemplo. |
| `requirements.txt` | As versões usadas na aula. |

## Instalar o LangGraph

Os comandos da aula rodaram com o LangGraph 1.2.21 e o langchain-core 1.8.0, as mesmas versões das aulas 04 a 07. Em 25 de novembro de 2026, o PyPI já tinha o LangGraph 1.2.24 e o langchain-core 1.8.4; o `requirements.txt` fixa as versões testadas. O langchain-core pede Python 3.11 ou mais novo. Se você já criou o ambiente nas aulas 04 a 07, pode usar o mesmo.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Se o `python3 --version` mostrar um Python mais velho que o 3.11, crie o ambiente com o Python novo, por exemplo `python3.11 -m venv .venv`. No Windows, troque as duas primeiras linhas por `py -3.11 -m venv .venv` e `.venv\Scripts\activate`. Com o ambiente ativo, os comandos abaixo usam o Python dele. Nada aqui chama um modelo de linguagem nem precisa de chave ou internet depois da instalação.

## Comandos

```bash
python3 queda.py
python3 queda.py chave-nova
python3 queda.py chave-do-pedido
python3 historia.py versao_do_colega.py
python3 historia.py
python3 testar_retomada.py
python3 testar_retomada.py versao_do_colega.py
```

Com a versão do colega, o `testar_retomada.py` termina em `5 de 10 testes passaram` e sai com código 1. É de propósito: são as falhas que a aula mostra.

Os reembolsos ficam num `InMemorySaver`, na memória do Python. Cada vez que você roda, eles começam do zero. Dentro de um teste, o reinício do servidor é um `Atendimento` novo com o mesmo `Banco` e a mesma `Operadora`. A operadora e o mensageiro do kit são listas na memória: nenhum dinheiro e nenhuma mensagem saem de verdade.

Para o exercício, copie o `servidor.py` para `aviso.py`, acrescente o aviso e rode:

```bash
python3 meus_testes.py
python3 meus_testes.py uma_copia_quebrada.py
python3 testar_retomada.py aviso.py
```

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.
