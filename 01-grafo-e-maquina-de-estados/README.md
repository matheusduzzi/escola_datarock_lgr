# Kit do curso Agentes com LangGraph

Os arquivos que você usa nas aulas: o diagnóstico e os pedidos e mensagens da Loja Exemplo.

## Como o kit está organizado

| Pasta | O que tem |
|---|---|
| `00-apresentacao/` | O [diagnóstico](00-apresentacao/diagnostico.md), o programa e o teste da tarefa 1 e a [folha de respostas](00-apresentacao/minhas-respostas.md). |
| `dados/loja/` | 120 pedidos e 59 mensagens de clientes. Ver [dados/loja/LEIA-ME.md](dados/loja/LEIA-ME.md). |
| `NN-titulo/` | Uma pasta por aula, com o número e o título da aula. Elas entram no kit junto com as aulas. |

Os comandos das aulas rodam de dentro da pasta da aula. Quando uma aula usa os pedidos, ela diz o caminho, por exemplo `../dados/loja/pedidos.csv`.

## Do que você precisa

- Python 3.9 ou mais novo para o diagnóstico. Ele só usa a biblioteca padrão: não precisa instalar nada.
- Um editor de código e um terminal.

O LangGraph entra na aula 02. Ele pede um Python mais novo que o do diagnóstico. A aula 02 traz a versão testada, o Python mínimo e o comando de instalação. As aulas rodam com um modelo falso, sem chave de API e sem internet.

Veja se o seu Python roda o kit:

```bash
cd 00-apresentacao
python3 testar_tarefa1.py
```

Antes de você escrever a função da tarefa 1, a saída termina com `0 de 6 testes passaram` e cada teste mostra `NotImplementedError`. Isso quer dizer que o Python achou os arquivos. Se aparecer `No such file or directory`, você não está dentro de `00-apresentacao/`. No Windows, troque `python3` por `py`.

## Se precisar de ajuda

Deixe um comentário na aula. Conte o objetivo, o comando que você rodou, a saída que apareceu e o que já tentou, sem dados pessoais.

## Licença

A licença de uso e redistribuição do kit ainda vai ser definida pela Escola Datarock. Até lá, use os arquivos para estudar o curso. A Loja Exemplo é inventada, e os pedidos e mensagens foram gerados para o curso.
