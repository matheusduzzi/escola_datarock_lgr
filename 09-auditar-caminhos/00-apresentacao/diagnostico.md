# Diagnóstico: por onde começar em Agentes com LangGraph

A coordenadora do atendimento da Loja Exemplo quer um agente que resolva reembolsos. Até 200 reais, ele reembolsa sozinho. Acima disso, alguém do financeiro aprova. O medo dela tem nome: o mesmo reembolso sair duas vezes porque o sistema caiu no meio. Antes de montar o primeiro grafo, eu refiz seis contas que o curso usa desde a aula 01. As tarefas abaixo são essas contas.

As cinco primeiras vêm do curso Agentes de IA em produção. São Python com teste, estados de um fluxo, modelo falso, falha no meio de uma ação e aprovação humana. A sexta é sobre conversa salva e quem pode ver cada conversa. Se ela travar, tudo bem: a aula 05 ensina essa parte.

O diagnóstico não é prova e não tem nota. Ele mostra por onde você começa. Anote na [folha de respostas](minhas-respostas.md) a conta que fez, o comando que rodou e a saída que apareceu. Só depois compare com as respostas.

A tarefa 1 roda no terminal, de dentro da pasta `00-apresentacao/`. As outras são de lápis e papel. No Windows, troque `python3` por `py`.

## Tarefa 1. O reembolso que não pode sair duas vezes

O arquivo `../dados/loja/pedidos.csv` tem 120 pedidos da loja. O [LEIA-ME](../dados/loja/LEIA-ME.md) explica cada coluna. Em `tarefa1.py`, escreva a função `reembolsar(pedidos, registro, id_pedido, valor, chave)`. Ela recebe os pedidos, a lista de reembolsos já gravados e o pedido de reembolso. A chave é o código que o atendimento manda junto com cada pedido de reembolso.

| Situação | O que a função faz |
|---|---|
| o pedido não existe | para com `ValueError` |
| o valor é zero, negativo ou maior que o valor do pedido | para com `ValueError` |
| a chave já está no registro, com o mesmo pedido e o mesmo valor | retorna `'repetido'` e não grava nada |
| a chave já está no registro, com outro pedido ou outro valor | para com `ValueError` |
| nenhum dos casos acima | acrescenta `{'chave': ..., 'id_pedido': ..., 'valor': ...}` ao registro e retorna `'feito'` |

A função não pode mudar os pedidos que recebeu.

Rode:

```bash
python3 tarefa1.py
python3 testar_tarefa1.py
```

Enquanto a função não existe, os dois comandos param com `NotImplementedError`. Quando os seis testes passarem, anote:

1. As cinco linhas que `tarefa1.py` mostrou.
2. Por que a segunda chamada do pedido 52 não pode gravar outra linha?
3. Por que parar com erro quando a mesma chave chega com outro pedido, em vez de responder `'repetido'`?

## Tarefa 2. Onde o fluxo trava

Esta tabela é o fluxo do atendimento que eu achei num documento antigo. Cada linha diz: estando neste estado, se acontece tal coisa, o fluxo vai para tal estado. Ele começa em `inicio` e termina em `fim`.

| Estado | Quando acontece | Vai para |
|---|---|---|
| `inicio` | chega uma mensagem | `classificar` |
| `classificar` | é sobre um pedido | `consultar_pedido` |
| `classificar` | é uma troca | `pedir_foto` |
| `consultar_pedido` | achou o pedido | `responder` |
| `consultar_pedido` | não achou o pedido | `responder` |
| `pedir_foto` | a foto chegou | `abrir_troca` |
| `pedir_foto` | a foto não chegou | `pedir_foto` |
| `abrir_troca` | a troca foi aberta | `responder` |
| `responder` | a resposta foi enviada | `fim` |
| `passar_para_pessoa` | uma pessoa atendeu | `fim` |

1. Que estado nunca é alcançado a partir de `inicio`?
2. Chega a mensagem "vocês abrem no feriado?". Ela não é pedido nem troca. Para onde vai o fluxo?
3. Que estado pode rodar para sempre? O que você muda para ele terminar?
4. Desenhe o fluxo corrigido, com as duas mudanças.

## Tarefa 3. O que o teste com modelo falso mostra

Eu testei o agente com um modelo falso. Ele não chama nenhum modelo de verdade: só repete respostas escritas antes. Na primeira chamada, ele pede a ferramenta `consultar_pedido(id_pedido=7)`. Na segunda, ele escreve "Seu pedido 7 foi entregue". O teste passou: a ferramenta rodou uma vez e a conversa terminou com texto.

Para cada frase, diga se esse teste mostra que ela é verdade:

- a) O agente chama a ferramenta quando o modelo pede.
- b) Um modelo de verdade vai pedir `consultar_pedido` quando o cliente escrever "cadê minha cadeira?".
- c) O loop entre modelo e ferramenta termina quando o modelo responde com texto.
- d) A resposta que o cliente lê usa o status que a ferramenta trouxe.
- e) Cada conversa custa menos de um centavo.

## Tarefa 4. O estorno que talvez tenha saído

O agente aprovou um reembolso do pedido 7, de 850 reais. Este é o registro da execução:

```text
10:02:01 passo 1  classificar: reembolso
10:02:02 passo 2  validar pedido 7, valor 850,00: ok
10:02:03 passo 3  aprovação do financeiro: aprovado
10:02:04 passo 4  chamar pagamentos.estornar(pedido=7, valor=850,00)
10:02:34 passo 4  tempo esgotado, sem resposta do serviço
10:02:35 o processo reiniciou e o fluxo voltou para o passo 4
```

1. O estorno aconteceu? O que o registro deixa você afirmar?
2. Se o passo 4 rodar de novo do jeito que está, quanto a cliente pode receber no pior caso?
3. O que precisa existir para repetir o passo 4 sem esse risco?
4. Que passos não precisam rodar de novo? Por quê?

## Tarefa 5. Quem precisa de aprovação

A regra do financeiro: reembolso de até 200 reais sai sozinho. Acima disso, o fluxo para e espera uma pessoa. Só a resposta `aprovado` libera o reembolso. Qualquer outra resposta nega. Os valores abaixo são os do arquivo de pedidos.

| Pedido | Valor | Resposta da pessoa |
|---|---|---|
| 52 | 79,90 | nenhuma pergunta foi feita |
| 42 | 200,00 | nenhuma pergunta foi feita |
| 44 | 259,00 | `aprovado` |
| 7 | 850,00 | `acho que pode` |
| 54 | 850,00 | ainda não respondeu |
| 29 | 349,90 | `rejeitado` |

1. Quais pedidos precisam de aprovação?
2. Diga como cada pedido termina: reembolsado, negado ou ainda esperando.
3. Quanto foi reembolsado no total?
4. No arquivo `../dados/loja/pedidos.csv` inteiro, quantos pedidos passariam pela aprovação? Pode usar Python ou planilha.

## Tarefa 6. A conversa de quem?

O agente guarda cada conversa com um código, o `thread_id`. Ao voltar com o mesmo código, o agente lê o histórico daquela conversa.

A Cliente 0143 abriu a conversa `t-0143-a` e perguntou do pedido 7, que é dela. Dias depois, o Cliente 0050 entrou logado na conta dele. Ele mandou uma mensagem com o mesmo `thread_id` `t-0143-a`, que alguém copiou de um link. A pergunta foi: "qual o valor do meu último pedido?".

1. O que o histórico da conversa traz para o agente nesse momento?
2. Guardar cada conversa separada resolve quem pode ver cada pedido? Por quê?
3. Onde você coloca a regra que impede o Cliente 0050 de ver o pedido 7?
